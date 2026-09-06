import os
import zipfile
import pandas as pd
from typing import Optional

RAW_WORKFORCE_DIR = "data/raw/workforce"
RAW_WORKFORCE_CSV = os.path.join(RAW_WORKFORCE_DIR, "WA_Fn-UseC_-HR-Employee-Attrition.csv")
REFERENCE_ARCHIVE = "reference/archive (7).zip"
ARCHIVE_CSV_NAME = "WA_Fn-UseC_-HR-Employee-Attrition.csv"

EXPECTED_ROWS = 1470
EXPECTED_COLS = 35
EXPECTED_ATTRITION_YES = 237
EXPECTED_ATTRITION_NO = 1233


def ensure_ibm_hr_extracted(
    csv_path: str = RAW_WORKFORCE_CSV,
    archive_path: str = REFERENCE_ARCHIVE,
) -> str:
    """
    Ensures that the IBM HR dataset CSV is extracted from the authoritative archive.
    If not already extracted, extracts it from reference/archive (7).zip.
    """
    if not os.path.exists(csv_path):
        if not os.path.exists(archive_path):
            raise FileNotFoundError(
                f"Authoritative archive '{archive_path}' not found. "
                "Cannot extract IBM HR dataset."
            )
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with zipfile.ZipFile(archive_path, "r") as z:
            if ARCHIVE_CSV_NAME not in z.namelist():
                raise KeyError(
                    f"'{ARCHIVE_CSV_NAME}' not found inside archive '{archive_path}'."
                )
            z.extract(ARCHIVE_CSV_NAME, os.path.dirname(csv_path))
            
    return csv_path


def load_ibm_hr_raw(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Loads and validates the IBM HR Employee Attrition raw dataset.
    Enforces strict assertions on dimensions, missingness, and target distribution.
    
    Returns:
    --------
    pd.DataFrame: Validated raw employee records.
    """
    path_to_load = csv_path or RAW_WORKFORCE_CSV
    ensure_ibm_hr_extracted(csv_path=path_to_load)
    
    df = pd.read_csv(path_to_load)
    
    # 1. Dimension assertions
    assert df.shape[0] == EXPECTED_ROWS, (
        f"Row count mismatch: expected {EXPECTED_ROWS}, got {df.shape[0]}"
    )
    assert df.shape[1] == EXPECTED_COLS, (
        f"Column count mismatch: expected {EXPECTED_COLS}, got {df.shape[1]}"
    )
    
    # 2. Completeness assertion (0 nulls)
    total_nulls = df.isnull().sum().sum()
    assert total_nulls == 0, (
        f"Dataset contains unexpected missing values: {total_nulls} nulls found."
    )
    
    # 3. Target integrity assertions
    assert "Attrition" in df.columns, "Target column 'Attrition' not found in dataset."
    attrition_vals = set(df["Attrition"].unique())
    assert attrition_vals == {"Yes", "No"}, (
        f"Unexpected target values: {attrition_vals}"
    )
    
    counts = df["Attrition"].value_counts().to_dict()
    assert counts.get("Yes") == EXPECTED_ATTRITION_YES, (
        f"Expected {EXPECTED_ATTRITION_YES} 'Yes' attrition records, got {counts.get('Yes')}"
    )
    assert counts.get("No") == EXPECTED_ATTRITION_NO, (
        f"Expected {EXPECTED_ATTRITION_NO} 'No' attrition records, got {counts.get('No')}"
    )
    
    return df
