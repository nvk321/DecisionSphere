import zipfile
import os
import io
import json
import pandas as pd
import numpy as np

REFERENCE_DIR = r"d:\Projects\DecisionSphere\reference"

def profile_dataframe(df, name, target_cols=None, date_cols=None):
    profile = {
        "dataset_name": name,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "memory_mb": round(float(df.memory_usage(deep=True).sum()) / (1024 * 1024), 2),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns_info": {},
        "target_distributions": {},
        "temporal_coverage": {}
    }
    
    # Missingness and types
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_pct = round(null_count / len(df) * 100, 2)
        n_unique = int(df[col].nunique())
        dtype = str(df[col].dtype)
        
        sample_vals = df[col].dropna().unique()[:3].tolist()
        # Convert any non-serializable objects to str
        sample_vals = [str(x) for x in sample_vals]
        
        profile["columns_info"][col] = {
            "dtype": dtype,
            "null_count": null_count,
            "null_pct": null_pct,
            "n_unique": n_unique,
            "sample_values": sample_vals
        }
        
    # Date profiling
    if date_cols:
        for dcol in date_cols:
            if dcol in df.columns:
                try:
                    s = pd.to_datetime(df[dcol], errors='coerce')
                    s_valid = s.dropna()
                    if len(s_valid) > 0:
                        profile["temporal_coverage"][dcol] = {
                            "min_date": str(s_valid.min()),
                            "max_date": str(s_valid.max()),
                            "days_span": int((s_valid.max() - s_valid.min()).days),
                            "valid_date_count": int(len(s_valid)),
                            "invalid_date_count": int(len(df) - len(s_valid))
                        }
                except Exception as e:
                    profile["temporal_coverage"][dcol] = f"Error parsing date: {str(e)}"
                    
    # Target distribution
    if target_cols:
        for tcol in target_cols:
            if tcol in df.columns:
                if df[tcol].nunique() <= 10 or df[tcol].dtype == 'object':
                    val_counts = df[tcol].value_counts(dropna=False, normalize=True).to_dict()
                    profile["target_distributions"][tcol] = {
                        "type": "categorical",
                        "distribution": {str(k): round(float(v), 4) for k, v in val_counts.items()}
                    }
                else:
                    if pd.api.types.is_numeric_dtype(df[tcol]):
                        desc = df[tcol].describe().to_dict()
                        profile["target_distributions"][tcol] = {
                            "type": "numerical",
                            "stats": {k: round(float(v), 2) for k, v in desc.items()}
                        }
                    else:
                        val_counts = df[tcol].value_counts(dropna=False, normalize=True).head(10).to_dict()
                        profile["target_distributions"][tcol] = {
                            "type": "categorical_or_string",
                            "distribution": {str(k): round(float(v), 4) for k, v in val_counts.items()}
                        }
                    
    return profile

def run_audit():
    results = {}
    
    # 1. IBM HR Attrition
    print("Auditing IBM HR Attrition dataset...")
    hr_zip = os.path.join(REFERENCE_DIR, "archive (7).zip")
    with zipfile.ZipFile(hr_zip) as z:
        with z.open("WA_Fn-UseC_-HR-Employee-Attrition.csv") as f:
            df_hr = pd.read_csv(f)
            results["IBM_HR"] = profile_dataframe(df_hr, "IBM HR Analytics Employee Attrition", target_cols=["Attrition"])

    # 2. Walmart Recruiting Store Sales
    print("Auditing Walmart Store Sales dataset...")
    wm_zip = os.path.join(REFERENCE_DIR, "archive (1).zip")
    with zipfile.ZipFile(wm_zip) as z:
        with z.open("train.csv") as f:
            df_wm_train = pd.read_csv(f)
            results["Walmart_Train"] = profile_dataframe(df_wm_train, "Walmart Sales Train", target_cols=["Weekly_Sales"], date_cols=["Date"])
        with z.open("features.csv") as f:
            df_wm_feat = pd.read_csv(f)
            results["Walmart_Features"] = profile_dataframe(df_wm_feat, "Walmart Features", date_cols=["Date"])
        with z.open("stores.csv") as f:
            df_wm_stores = pd.read_csv(f)
            results["Walmart_Stores"] = profile_dataframe(df_wm_stores, "Walmart Stores")

    # 3. Rossmann Store Sales
    print("Auditing Rossmann Store Sales dataset...")
    ross_zip = os.path.join(REFERENCE_DIR, "rossmann-store-sales.zip")
    with zipfile.ZipFile(ross_zip) as z:
        with z.open("train.csv") as f:
            df_ross_train = pd.read_csv(f)
            results["Rossmann_Train"] = profile_dataframe(df_ross_train, "Rossmann Sales Train", target_cols=["Sales", "Customers", "Open"], date_cols=["Date"])
        with z.open("store.csv") as f:
            df_ross_store = pd.read_csv(f)
            results["Rossmann_Stores"] = profile_dataframe(df_ross_store, "Rossmann Store Info")

    # 4. Corporacion Favorita Store Sales
    print("Auditing Corporacion Favorita Store Sales dataset...")
    fav_zip = os.path.join(REFERENCE_DIR, "store-sales-time-series-forecasting (1).zip")
    with zipfile.ZipFile(fav_zip) as z:
        # train.csv is ~116MB, let's load first 200,000 rows or inspect full rows count
        # Let's count rows and sample
        with z.open("train.csv") as f:
            df_fav_train = pd.read_csv(f, nrows=200000)
            results["Favorita_Train_Sample200k"] = profile_dataframe(df_fav_train, "Corporacion Favorita Train (200k sample)", target_cols=["sales", "onpromotion"], date_cols=["date"])
        with z.open("oil.csv") as f:
            df_oil = pd.read_csv(f)
            results["Favorita_Oil"] = profile_dataframe(df_oil, "Favorita Oil Prices", date_cols=["date"])
        with z.open("holidays_events.csv") as f:
            df_hol = pd.read_csv(f)
            results["Favorita_Holidays"] = profile_dataframe(df_hol, "Favorita Holidays", date_cols=["date"])
        with z.open("stores.csv") as f:
            df_fav_stores = pd.read_csv(f)
            results["Favorita_Stores"] = profile_dataframe(df_fav_stores, "Favorita Stores")

    # 5. DataCo Supply Chain
    print("Auditing DataCo Supply Chain dataset...")
    dataco_zip = os.path.join(REFERENCE_DIR, "archive (2).zip")
    with zipfile.ZipFile(dataco_zip) as z:
        with z.open("DataCoSupplyChainDataset.csv") as f:
            # DataCo can have non-standard encoding, typically ISO-8859-1 or latin1
            try:
                df_dataco = pd.read_csv(f, encoding='utf-8')
            except UnicodeDecodeError:
                f.seek(0)
                df_dataco = pd.read_csv(f, encoding='latin1')
            results["DataCo_SupplyChain"] = profile_dataframe(
                df_dataco, "DataCo Smart Supply Chain",
                target_cols=["Late_delivery_risk", "Delivery Status", "Days for shipping (real)", "Days for shipment (scheduled)"],
                date_cols=["order date (DateOrders)", "shipping date (DateOrders)"]
            )

    # 6. SCMS Delivery History (alternative supply chain dataset)
    print("Auditing SCMS Delivery History dataset...")
    scms_zip = os.path.join(REFERENCE_DIR, "archive (4).zip")
    with zipfile.ZipFile(scms_zip) as z:
        with z.open("SCMS_Delivery_History_Dataset.csv") as f:
            try:
                df_scms = pd.read_csv(f, encoding='utf-8')
            except UnicodeDecodeError:
                f.seek(0)
                df_scms = pd.read_csv(f, encoding='latin1')
            results["SCMS_Delivery"] = profile_dataframe(
                df_scms, "SCMS Delivery History",
                target_cols=["Shipment Mode", "Scheduled Delivery Date", "Delivered to Client Date"],
                date_cols=["Scheduled Delivery Date", "Delivered to Client Date"]
            )

    out_json = r"C:\Users\kusha\.gemini\antigravity-ide\brain\f58c1888-f6cb-4c39-b066-b682b9cfdf6b\scratch\audit_summary.json"
    with open(out_json, "w", encoding="utf-8") as out_f:
        json.dump(results, out_f, indent=2)
    print(f"Audit completed successfully. Results saved to {out_json}")

if __name__ == "__main__":
    run_audit()
