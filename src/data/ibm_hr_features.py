import pandas as pd
import numpy as np
from typing import Tuple, List, Dict
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# -------------------------------------------------------------------------
# EXPLICIT LEAKAGE & EXCLUSION REGISTRY
# -------------------------------------------------------------------------

EXCLUDED_INVARIANT_COLUMNS = [
    "EmployeeCount",     # Constant: all rows equal 1 (zero variance)
    "StandardHours",     # Constant: all rows equal 80 (zero variance)
    "Over18",            # Constant: all rows equal 'Y' (zero variance)
]

EXCLUDED_SURROGATE_COLUMNS = [
    "EmployeeNumber",    # Unique database surrogate identifier (1 to 2,068) - memorization risk
]

TARGET_COLUMN = "Attrition"

ALL_EXCLUDED_COLUMNS = (
    EXCLUDED_INVARIANT_COLUMNS
    + EXCLUDED_SURROGATE_COLUMNS
    + [TARGET_COLUMN]
)

# -------------------------------------------------------------------------
# VALID EMPLOYEE-TIME PREDICTOR REGISTRY (EXACTLY 30 PREDICTORS)
# -------------------------------------------------------------------------

NUMERICAL_FEATURES = [
    "Age",                       # Continuous age in years (18 to 60)
    "DailyRate",                 # Compensation structure metric
    "DistanceFromHome",          # Commute distance (1 to 29 miles)
    "Education",                 # Qualification level (1 to 5)
    "EnvironmentSatisfaction",   # Periodic pulse survey rating (1 to 4)
    "HourlyRate",                # Compensation structure metric
    "JobInvolvement",            # Survey engagement rating (1 to 4)
    "JobLevel",                  # Organizational seniority level (1 to 5)
    "JobSatisfaction",           # Survey job satisfaction rating (1 to 4)
    "MonthlyIncome",             # Base monthly compensation ($1,009 to $19,999)
    "MonthlyRate",               # Compensation structure metric
    "NumCompaniesWorked",        # Career mobility history (0 to 9)
    "PercentSalaryHike",         # Last salary hike percentage (11% to 25%)
    "PerformanceRating",         # Review rating (3 to 4)
    "RelationshipSatisfaction",  # Survey team relationship rating (1 to 4)
    "StockOptionLevel",          # Equity compensation tier (0 to 3)
    "TotalWorkingYears",         # Cumulative working years (0 to 40)
    "TrainingTimesLastYear",     # Professional development events (0 to 6)
    "WorkLifeBalance",           # Survey work-life balance rating (1 to 4)
    "YearsAtCompany",            # Organizational tenure (0 to 40)
    "YearsInCurrentRole",        # Tenure in current role (0 to 18)
    "YearsSinceLastPromotion",   # Promotion velocity / stagnancy proxy (0 to 15)
    "YearsWithCurrManager",      # Manager relationship stability (0 to 17)
]

CATEGORICAL_FEATURES = [
    "BusinessTravel",            # Work travel frequency ('Travel_Rarely', 'Travel_Frequently', 'Non-Travel')
    "Department",                # Business unit ('Sales', 'Research & Development', 'Human Resources')
    "EducationField",            # Discipline ('Life Sciences', 'Medical', 'Marketing', etc.)
    "Gender",                    # Demographic ('Female', 'Male')
    "JobRole",                   # 9 discrete job roles
    "MaritalStatus",             # Demographic ('Single', 'Married', 'Divorced')
    "OverTime",                  # Primary operational workload lever ('Yes', 'No')
]

ALL_PREDICTOR_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
assert len(ALL_PREDICTOR_FEATURES) == 30, (
    f"Expected exactly 30 modeling predictors, got {len(ALL_PREDICTOR_FEATURES)}"
)


def create_ibm_hr_features(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs the modeling feature matrix from raw IBM HR records.
    Strictly excludes zero-variance invariants, surrogate identifiers, and targets.
    
    Returns:
    --------
    pd.DataFrame: Contains 30 clean predictors plus binary target 'target_attrition'.
    """
    df = df_raw.copy()
    
    # 1. Verification of raw input columns
    for col in ALL_EXCLUDED_COLUMNS:
        assert col in df.columns, f"Expected column '{col}' missing from raw IBM HR dataset."
        
    # 2. Binary target construction: 'Yes' -> 1, 'No' -> 0
    df["target_attrition"] = (df[TARGET_COLUMN] == "Yes").astype(int)
    
    # 3. Enforce data types on retained features
    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype(str).str.strip()
        
    for col in NUMERICAL_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        
    # 4. Construct final modeling DataFrame
    keep_cols = ALL_PREDICTOR_FEATURES + ["target_attrition"]
    df_feat = df[keep_cols].copy()
    
    # 5. Strict anti-leakage and invariant validation
    for excluded in [col for col in ALL_EXCLUDED_COLUMNS if col != TARGET_COLUMN]:
        assert excluded not in df_feat.columns, (
            f"CRITICAL ERROR: Prohibited column '{excluded}' detected in modeling matrix!"
        )
    assert TARGET_COLUMN not in df_feat.columns, (
        f"CRITICAL ERROR: Raw string target '{TARGET_COLUMN}' detected in features!"
    )
    
    # Verify no feature has zero variance
    for col in NUMERICAL_FEATURES:
        assert df_feat[col].std() > 0, f"Numerical feature '{col}' has zero variance!"
    for col in CATEGORICAL_FEATURES:
        assert df_feat[col].nunique() > 1, f"Categorical feature '{col}' has zero variance!"
        
    return df_feat


def split_stratified_ibm_hr(
    df_feat: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits the IBM HR feature matrix into stratified Train, Validation, and Test partitions.
    Since IBM HR is cross-sectional without timestamps, stratification on target_attrition
    ensures identical minority attrition class representation across all partitions.
    
    Guarantees:
    - Zero sample overlap between partitions.
    - Zero preprocessing is performed prior to splitting.
    
    Returns:
    --------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: (train_df, val_df, test_df)
    """
    assert np.isclose(train_ratio + val_ratio + test_ratio, 1.0), "Split ratios must sum to 1.0"
    
    y = df_feat["target_attrition"]
    
    # First split: Train (70%) vs Temp (30%)
    temp_ratio = val_ratio + test_ratio
    train_df, temp_df = train_test_split(
        df_feat,
        test_size=temp_ratio,
        stratify=y,
        random_state=random_state,
    )
    
    # Second split: Val (15% of total) vs Test (15% of total)
    val_proportion_of_temp = val_ratio / temp_ratio
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1.0 - val_proportion_of_temp),
        stratify=temp_df["target_attrition"],
        random_state=random_state,
    )
    
    # Verify complete partition isolation
    train_idx = set(train_df.index)
    val_idx = set(val_df.index)
    test_idx = set(test_df.index)
    
    assert len(train_idx.intersection(val_idx)) == 0, "Overlap detected between Train and Validation!"
    assert len(train_idx.intersection(test_idx)) == 0, "Overlap detected between Train and Test!"
    assert len(val_idx.intersection(test_idx)) == 0, "Overlap detected between Validation and Test!"
    assert len(train_df) + len(val_df) + len(test_df) == len(df_feat), "Row count mismatch across splits!"
    
    return train_df.copy(), val_df.copy(), test_df.copy()


def build_workforce_preprocessor(
    numerical_cols: List[str] = None,
    categorical_cols: List[str] = None,
) -> ColumnTransformer:
    """
    Builds the ColumnTransformer for the Workforce pipeline.
    Applies StandardScaler to numerical features and OneHotEncoder to categorical features.
    
    Must be fitted ONLY on the training partition to prevent leakage.
    """
    num_cols = numerical_cols if numerical_cols is not None else NUMERICAL_FEATURES
    cat_cols = categorical_cols if categorical_cols is not None else CATEGORICAL_FEATURES
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                cat_cols,
            ),
        ],
        remainder="drop",
    )
    return preprocessor
