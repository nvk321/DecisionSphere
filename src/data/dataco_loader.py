import os
import zipfile
import pandas as pd
import numpy as np

DATACO_ARCHIVE_PATH = "reference/archive (2).zip"
DATACO_RAW_DIR = "data/raw/dataco"
DATACO_CSV_NAME = "DataCoSupplyChainDataset.csv"

def extract_dataco_raw(archive_path: str = DATACO_ARCHIVE_PATH, target_dir: str = DATACO_RAW_DIR) -> str:
    """
    Extracts DataCoSupplyChainDataset.csv from the reference archive if not already present.
    Returns the absolute or relative path to the extracted CSV file.
    """
    os.makedirs(target_dir, exist_ok=True)
    csv_path = os.path.join(target_dir, DATACO_CSV_NAME)
    
    if not os.path.exists(csv_path):
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"DataCo source archive not found at: {archive_path}")
        
        print(f"Extracting {DATACO_CSV_NAME} from {archive_path} to {target_dir}...")
        with zipfile.ZipFile(archive_path, "r") as z:
            z.extract(DATACO_CSV_NAME, path=target_dir)
            if "DescriptionDataCoSupplyChain.csv" in z.namelist():
                z.extract("DescriptionDataCoSupplyChain.csv", path=target_dir)
        print("Extraction complete.")
        
    return csv_path

def load_dataco_raw(data_dir: str = DATACO_RAW_DIR, archive_path: str = DATACO_ARCHIVE_PATH) -> pd.DataFrame:
    """
    Loads raw DataCo Supply Chain dataset with Latin1 encoding and explicit validation.
    Enforces shape integrity (asserts 180,519 rows x 53 columns) and binary target format.
    """
    csv_path = os.path.join(data_dir, DATACO_CSV_NAME)
    if not os.path.exists(csv_path):
        csv_path = extract_dataco_raw(archive_path=archive_path, target_dir=data_dir)
        
    df = pd.read_csv(csv_path, encoding="latin1", low_memory=False)
    
    # 1. Structural integrity verification
    expected_rows = 180519
    expected_cols = 53
    if len(df) != expected_rows or len(df.columns) != expected_cols:
        raise ValueError(
            f"DataCo dataset dimension mismatch: expected ({expected_rows}, {expected_cols}), got {df.shape}"
        )
        
    # 2. Target integrity verification
    if "Late_delivery_risk" not in df.columns:
        raise KeyError("Target column 'Late_delivery_risk' not found in DataCo dataset.")
        
    unique_targets = set(df["Late_delivery_risk"].dropna().unique())
    if unique_targets != {0, 1}:
        raise ValueError(f"Target 'Late_delivery_risk' must be binary {{0, 1}}, found: {unique_targets}")
        
    # 3. Parse order date and sort chronologically
    df["order_dt"] = pd.to_datetime(df["order date (DateOrders)"], format="%m/%d/%Y %H:%M")
    df = df.sort_values("order_dt").reset_index(drop=True)
    
    return df
