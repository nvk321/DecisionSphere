import os
import pandas as pd
import numpy as np

def load_rossmann_raw(data_dir: str = "data/raw/rossmann"):
    """
    Loads raw Rossmann train and store datasets.
    Ensures chronological ascending sort order and standardizes datatypes.
    """
    train_path = os.path.join(data_dir, "train.csv")
    store_path = os.path.join(data_dir, "store.csv")
    
    if not os.path.exists(train_path) or not os.path.exists(store_path):
        raise FileNotFoundError(f"Rossmann data files not found in {data_dir}. Expected train.csv and store.csv.")
        
    df_train = pd.read_csv(train_path, low_memory=False)
    df_store = pd.read_csv(store_path)
    
    # 1. Parse dates and sort strictly ascending
    df_train["Date"] = pd.to_datetime(df_train["Date"])
    df_train = df_train.sort_values(["Date", "Store"]).reset_index(drop=True)
    
    # 2. Standardize StateHoliday to clean string
    df_train["StateHoliday"] = df_train["StateHoliday"].astype(str).str.strip()
    df_train["StateHoliday"] = df_train["StateHoliday"].replace({"0.0": "0", "": "0"})
    
    # 3. Ensure integer / float types
    df_train["Store"] = df_train["Store"].astype(int)
    df_train["DayOfWeek"] = df_train["DayOfWeek"].astype(int)
    df_train["Open"] = df_train["Open"].astype(int)
    df_train["Promo"] = df_train["Promo"].astype(int)
    df_train["SchoolHoliday"] = df_train["SchoolHoliday"].astype(int)
    df_train["Sales"] = df_train["Sales"].astype(float)
    
    return df_train, df_store

def merge_store_metadata(df_train: pd.DataFrame, df_store: pd.DataFrame) -> pd.DataFrame:
    """
    Merges store metadata with transactional sales records.
    Imputes missing values and creates domain-specific store indicators.
    """
    df_store = df_store.copy()
    
    # 1. Impute CompetitionDistance with median
    comp_dist_median = df_store["CompetitionDistance"].median()
    df_store["CompetitionDistance"] = df_store["CompetitionDistance"].fillna(comp_dist_median)
    df_store["LogCompetitionDistance"] = np.log1p(df_store["CompetitionDistance"])
    
    # 2. Merge on Store
    merged = pd.merge(df_train, df_store, on="Store", how="left")
    
    # 3. Calculate CompetitionOpen flag
    # If CompetitionOpenSinceYear and Month are present
    has_comp_date = merged["CompetitionOpenSinceYear"].notnull() & merged["CompetitionOpenSinceMonth"].notnull()
    comp_year = merged["CompetitionOpenSinceYear"].fillna(2099).astype(int)
    comp_month = merged["CompetitionOpenSinceMonth"].fillna(1).astype(int)
    
    comp_date = pd.to_datetime(
        comp_year.astype(str) + "-" + comp_month.astype(str).str.zfill(2) + "-01",
        errors="coerce"
    )
    merged["CompetitionOpen"] = ((merged["Date"] >= comp_date) & has_comp_date).astype(int)
    
    # 4. Calculate Promo2Active flag
    # Check if Promo2 is active in the given month and week
    merged["Promo2Active"] = 0
    promo2_mask = (merged["Promo2"] == 1) & merged["Promo2SinceYear"].notnull() & merged["PromoInterval"].notnull()
    
    if promo2_mask.any():
        month_abbr = merged.loc[promo2_mask, "Date"].dt.strftime("%b")
        p2_intervals = merged.loc[promo2_mask, "PromoInterval"]
        
        # Check if month abbreviation is contained in PromoInterval (e.g. 'Feb,May,Aug,Nov')
        is_promo_month = [abbr in interval for abbr, interval in zip(month_abbr, p2_intervals)]
        
        # Also check if current year/week is past Promo2 start
        p2_start_year = merged.loc[promo2_mask, "Promo2SinceYear"].astype(int)
        p2_start_week = merged.loc[promo2_mask, "Promo2SinceWeek"].astype(int)
        curr_year = merged.loc[promo2_mask, "Date"].dt.isocalendar().year
        curr_week = merged.loc[promo2_mask, "Date"].dt.isocalendar().week
        
        is_past_start = (curr_year > p2_start_year) | ((curr_year == p2_start_year) & (curr_week >= p2_start_week))
        
        active_indices = merged.loc[promo2_mask].index[np.array(is_promo_month) & is_past_start.values]
        merged.loc[active_indices, "Promo2Active"] = 1
        
    return merged
