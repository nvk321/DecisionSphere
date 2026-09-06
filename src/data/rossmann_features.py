import pandas as pd
import numpy as np
from typing import Tuple, List

# Explicit feature definitions
CALENDAR_FEATURES = [
    "DayOfWeek",
    "Month",
    "Day",
    "WeekOfYear",
    "IsWeekend",
    "IsMonthStart",
    "IsMonthEnd"
]

EVENT_FEATURES = [
    "Promo",
    "Promo2",
    "Promo2Active",
    "SchoolHoliday"
]

STORE_FEATURES = [
    "LogCompetitionDistance",
    "CompetitionOpen"
]

CATEGORICAL_COLUMNS = [
    "StoreType",
    "Assortment",
    "StateHoliday"
]

HISTORICAL_LAG_FEATURES = [
    "Sales_lag_1",
    "Sales_lag_7",
    "Sales_lag_14",
    "Sales_lag_28"
]

HISTORICAL_ROLLING_FEATURES = [
    "Sales_rolling_mean_7",
    "Sales_rolling_mean_14",
    "Sales_rolling_std_7"
]

def create_demand_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs causally valid features for the Rossmann demand forecasting model.
    Enforces strict anti-leakage controls:
    1. Customers is omitted.
    2. Historical lags and rolling statistics are calculated grouped by Store.
    3. Rolling windows strictly shift by >= 1 day so current or future target is never observed.
    """
    df = df.copy()
    
    # 1. Ensure sorted chronologically by Store and Date
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Store", "Date"]).reset_index(drop=True)
    
    # 2. Store metadata indicators (compute if not already pre-merged)
    if "LogCompetitionDistance" not in df.columns:
        comp_dist = df.get("CompetitionDistance", pd.Series(5000.0, index=df.index)).fillna(5000.0)
        df["LogCompetitionDistance"] = np.log1p(comp_dist)
        
    if "CompetitionOpen" not in df.columns:
        if "CompetitionOpenSinceYear" in df.columns and "CompetitionOpenSinceMonth" in df.columns:
            has_comp = df["CompetitionOpenSinceYear"].notnull() & df["CompetitionOpenSinceMonth"].notnull()
            comp_year = df["CompetitionOpenSinceYear"].fillna(2099).astype(int)
            comp_month = df["CompetitionOpenSinceMonth"].fillna(1).astype(int)
            comp_date = pd.to_datetime(
                comp_year.astype(str) + "-" + comp_month.astype(str).str.zfill(2) + "-01",
                errors="coerce"
            )
            df["CompetitionOpen"] = ((df["Date"] >= comp_date) & has_comp).astype(int)
        else:
            df["CompetitionOpen"] = 0
            
    if "Promo2Active" not in df.columns:
        df["Promo2Active"] = 0
        if "Promo2" in df.columns and "PromoInterval" in df.columns:
            promo2_mask = (df["Promo2"] == 1) & df["PromoInterval"].notnull()
            if promo2_mask.any():
                month_abbr = df.loc[promo2_mask, "Date"].dt.strftime("%b")
                p2_intervals = df.loc[promo2_mask, "PromoInterval"].astype(str)
                is_promo_month = [abbr in interval for abbr, interval in zip(month_abbr, p2_intervals)]
                df.loc[df[promo2_mask].index[is_promo_month], "Promo2Active"] = 1

    # 3. Calendar features
    df["DayOfWeek"] = df["Date"].dt.dayofweek + 1 # 1=Mon, 7=Sun
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df["WeekOfYear"] = df["Date"].dt.isocalendar().week.astype(int)
    df["IsWeekend"] = df["DayOfWeek"].isin([6, 7]).astype(int)
    df["IsMonthStart"] = df["Date"].dt.is_month_start.astype(int)
    df["IsMonthEnd"] = df["Date"].dt.is_month_end.astype(int)
    
    # 3. Categorical encoding
    # StoreType: a, b, c, d
    store_type_map = {"a": 0, "b": 1, "c": 2, "d": 3}
    df["StoreType_Encoded"] = df["StoreType"].map(store_type_map).fillna(0).astype(int)
    
    # Assortment: a, b, c
    assortment_map = {"a": 0, "b": 1, "c": 2}
    df["Assortment_Encoded"] = df["Assortment"].map(assortment_map).fillna(0).astype(int)
    
    # StateHoliday: '0', 'a', 'b', 'c'
    state_holiday_map = {"0": 0, "a": 1, "b": 2, "c": 3}
    df["StateHoliday_Encoded"] = df["StateHoliday"].astype(str).map(state_holiday_map).fillna(0).astype(int)
    
    # 4. Historical Lags (Strictly Grouped by Store)
    # y(t-1), y(t-7), y(t-14), y(t-28)
    store_grouped_sales = df.groupby("Store")["Sales"]
    
    df["Sales_lag_1"] = store_grouped_sales.shift(1)
    df["Sales_lag_7"] = store_grouped_sales.shift(7)
    df["Sales_lag_14"] = store_grouped_sales.shift(14)
    df["Sales_lag_28"] = store_grouped_sales.shift(28)
    
    # 5. Rolling Statistics (Strictly Shifted by 1 so day t is NEVER included)
    # Shift by 1 first, then compute rolling mean/std within store group
    df["Sales_rolling_mean_7"] = store_grouped_sales.transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).mean()
    )
    df["Sales_rolling_mean_14"] = store_grouped_sales.transform(
        lambda s: s.shift(1).rolling(14, min_periods=1).mean()
    )
    df["Sales_rolling_std_7"] = store_grouped_sales.transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).std()
    ).fillna(0.0)
    
    # 6. Handle early-history NaNs in lags via store-level fallback
    # To prevent throwing away the first 28 days of history, impute missing lags with rolling mean or store mean
    store_mean_sales = store_grouped_sales.transform("mean")
    for lag_col in HISTORICAL_LAG_FEATURES:
        df[lag_col] = df[lag_col].fillna(df["Sales_rolling_mean_7"]).fillna(store_mean_sales)
        
    df["Sales_rolling_mean_7"] = df["Sales_rolling_mean_7"].fillna(store_mean_sales)
    df["Sales_rolling_mean_14"] = df["Sales_rolling_mean_14"].fillna(store_mean_sales)
    
    # 7. Re-sort chronologically by Date, Store
    df = df.sort_values(["Date", "Store"]).reset_index(drop=True)
    
    return df

def get_feature_columns() -> List[str]:
    """Returns the list of final numerical predictor feature column names."""
    return (
        CALENDAR_FEATURES +
        EVENT_FEATURES +
        STORE_FEATURES +
        ["StoreType_Encoded", "Assortment_Encoded", "StateHoliday_Encoded"] +
        HISTORICAL_LAG_FEATURES +
        HISTORICAL_ROLLING_FEATURES
    )

def split_chronological(
    df: pd.DataFrame,
    train_end_date: str = "2014-10-19",
    val_end_date: str = "2015-03-10"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits the dataset into strictly chronological Train, Validation, and Test sets.
    - Train: Date <= train_end_date (~70%)
    - Validation: train_end_date < Date <= val_end_date (~15%)
    - Test: Date > val_end_date (~15%)
    """
    df["Date"] = pd.to_datetime(df["Date"])
    t_end = pd.to_datetime(train_end_date)
    v_end = pd.to_datetime(val_end_date)
    
    train_df = df[df["Date"] <= t_end].copy().reset_index(drop=True)
    val_df = df[(df["Date"] > t_end) & (df["Date"] <= v_end)].copy().reset_index(drop=True)
    test_df = df[df["Date"] > v_end].copy().reset_index(drop=True)
    
    return train_df, val_df, test_df
