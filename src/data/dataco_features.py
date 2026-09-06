import pandas as pd
import numpy as np
from typing import Tuple, List, Dict

# -------------------------------------------------------------------------
# EXPLICIT LEAKAGE & EXCLUSION REGISTRY
# -------------------------------------------------------------------------

PROHIBITED_LOOKAHEAD_COLUMNS = [
    "Days for shipping (real)",        # Known only post-delivery; encodes target (real > scheduled)
    "Delivery Status",                 # 100% deterministic outcome category
    "shipping date (DateOrders)",      # Post-order dispatch timestamp
    "Order Status",                    # Realized fulfillment state
]

PROHIBITED_ACCOUNTING_COLUMNS = [
    "Benefit per order",               # Post-delivery accounting outcome
    "Order Profit Per Order",          # Realized financial margin
    "Order Item Profit Ratio",         # Calculated post-fulfillment ratio
    "Sales per customer",              # Net post-return customer sales
]

PROHIBITED_PII_SURROGATE_COLUMNS = [
    "Customer Email",
    "Customer Fname",
    "Customer Lname",
    "Customer Password",
    "Customer Street",
    "Customer Id",                     # High cardinality, pure memorization risk
    "Order Customer Id",               # Duplicate customer key
    "Order Id",                        # Pure transaction key (65,752 unique)
    "Order Item Id",                   # Row primary key (180,519 unique)
    "Order Item Cardprod Id",          # Duplicate product card key
    "Product Card Id",                 # Catalog surrogate key (87.7% unseen in test)
    "Product Category Id",             # Duplicate of Category Id
    "Product Description",             # 100% null
    "Order Zipcode",                   # 86.2% null
    "Product Image",                   # Static image URL string
    "Product Status",                  # Zero-variance constant (all 0)
]

ALL_EXCLUDED_COLUMNS = (
    PROHIBITED_LOOKAHEAD_COLUMNS
    + PROHIBITED_ACCOUNTING_COLUMNS
    + PROHIBITED_PII_SURROGATE_COLUMNS
)

# -------------------------------------------------------------------------
# VALID ORDER-TIME PREDICTOR REGISTRY
# -------------------------------------------------------------------------

NUMERICAL_FEATURES = [
    "days_for_shipment_scheduled",     # Planned SLA duration (0, 1, 2, 4 days) - core operational lever
    "order_item_quantity",             # Quantity ordered (1 to 5) - operational load indicator
    "order_item_product_price",        # Unit catalog price
    "order_item_discount_rate",        # Percentage discount applied at checkout
    "order_item_total",                # Net checkout transaction total
    "product_price",                   # Catalog list price
    "latitude",                        # Origin dispatch facility latitude
    "longitude",                       # Origin dispatch facility longitude
    "order_year",                      # Temporal trend component
    "order_month",                     # Seasonal monthly component
    "order_day_of_week",               # Day of week component (0=Monday, 6=Sunday)
    "order_hour",                      # Checkout hour of day (0 to 23)
]

CATEGORICAL_FEATURES = [
    "type",                            # Payment type (DEBIT, TRANSFER, PAYMENT, CASH)
    "shipping_mode",                   # Freight class (Standard Class, First Class, Second Class, Same Day)
    "customer_segment",                # Customer tier (Consumer, Corporate, Home Office)
    "customer_country",                # Buyer country (Puerto Rico, EE. UU.)
    "customer_state",                  # Buyer US state / territory code
    "market",                          # Destination global market (5 regions)
    "order_region",                    # Destination delivery region (23 regions)
    "order_country",                   # Destination country code
    "department_id",                   # Merchandise department ID (11 departments)
    "category_id",                     # Product category ID (51 categories)
]

ALL_PREDICTOR_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

# Verified calendar split boundaries
DEFAULT_TRAIN_END = "2016-12-31 23:59:59"
DEFAULT_VAL_END = "2017-06-30 23:59:59"

def create_dataco_features(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs legitimate order-time feature matrix from raw DataCo records.
    Strictly excludes all prohibited lookahead, post-fulfillment, PII, and surrogate variables.
    """
    df = df_raw.copy()
    
    # 1. Parse order timestamp if not already parsed
    if "order_dt" not in df.columns:
        df["order_dt"] = pd.to_datetime(df["order date (DateOrders)"], format="%m/%d/%Y %H:%M")
        
    # 2. Derive legitimate order-time temporal features
    df["order_year"] = df["order_dt"].dt.year.astype(int)
    df["order_month"] = df["order_dt"].dt.month.astype(int)
    df["order_day_of_week"] = df["order_dt"].dt.dayofweek.astype(int)
    df["order_hour"] = df["order_dt"].dt.hour.astype(int)
    
    # 3. Standardize column names for selected predictors
    column_mapping = {
        "Days for shipment (scheduled)": "days_for_shipment_scheduled",
        "Order Item Quantity": "order_item_quantity",
        "Order Item Product Price": "order_item_product_price",
        "Order Item Discount Rate": "order_item_discount_rate",
        "Order Item Total": "order_item_total",
        "Product Price": "product_price",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Type": "type",
        "Shipping Mode": "shipping_mode",
        "Customer Segment": "customer_segment",
        "Customer Country": "customer_country",
        "Customer State": "customer_state",
        "Market": "market",
        "Order Region": "order_region",
        "Order Country": "order_country",
        "Department Id": "department_id",
        "Category Id": "category_id",
        "Late_delivery_risk": "late_delivery_risk",
    }
    
    df = df.rename(columns=column_mapping)
    
    # 4. Enforce categorical datatypes as strings
    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype(str).str.strip()
        
    # 5. Enforce numerical datatypes as floats/ints
    for col in NUMERICAL_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        
    # 6. Assemble final modeling DataFrame: features + target + order_dt
    keep_cols = ALL_PREDICTOR_FEATURES + ["late_delivery_risk", "order_dt"]
    df_feat = df[keep_cols].copy()
    
    # 7. Verification: Ensure no prohibited column is present
    for prohibited in ALL_EXCLUDED_COLUMNS:
        if prohibited in df_feat.columns:
            raise RuntimeError(f"CRITICAL LEAKAGE ERROR: Prohibited column '{prohibited}' detected in feature matrix!")
            
    return df_feat

def split_chronological_dataco(
    df: pd.DataFrame,
    train_end: str = DEFAULT_TRAIN_END,
    val_end: str = DEFAULT_VAL_END
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Executes strict chronological forward time split on DataCo dataset.
    Guarantees: max(train) < min(val) < min(test) with zero temporal shuffling.
    
    Default boundaries:
    - Train: 2015-01-01 to 2016-12-31 (~69.4% / 125,200 rows)
    - Val:   2017-01-01 to 2017-06-30 (~17.1% / 30,950 rows)
    - Test:  2017-07-01 to 2018-01-31 (~13.5% / 24,369 rows)
    """
    if "order_dt" not in df.columns:
        raise KeyError("DataFrame must contain 'order_dt' for chronological splitting.")
        
    df_sorted = df.sort_values("order_dt").reset_index(drop=True)
    
    train_df = df_sorted[df_sorted["order_dt"] <= train_end].copy().reset_index(drop=True)
    val_df = df_sorted[(df_sorted["order_dt"] > train_end) & (df_sorted["order_dt"] <= val_end)].copy().reset_index(drop=True)
    test_df = df_sorted[df_sorted["order_dt"] > val_end].copy().reset_index(drop=True)
    
    # Assert strict forward temporal integrity
    assert train_df["order_dt"].max() < val_df["order_dt"].min(), "Temporal leak: train overlap with val"
    assert val_df["order_dt"].max() < test_df["order_dt"].min(), "Temporal leak: val overlap with test"
    assert len(train_df) + len(val_df) + len(test_df) == len(df_sorted), "Row count mismatch in temporal split"
    
    return train_df, val_df, test_df

def get_feature_columns() -> List[str]:
    """Returns the immutable list of legitimate order-time predictor feature names."""
    return list(ALL_PREDICTOR_FEATURES)

def get_numerical_features() -> List[str]:
    """Returns the list of numerical feature names."""
    return list(NUMERICAL_FEATURES)

def get_categorical_features() -> List[str]:
    """Returns the list of categorical feature names."""
    return list(CATEGORICAL_FEATURES)
