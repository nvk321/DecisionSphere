import os
import pandas as pd
import numpy as np

raw_dir = r"d:\Projects\DecisionSphere\data\raw\rossmann"
train_path = os.path.join(raw_dir, "train.csv")
store_path = os.path.join(raw_dir, "store.csv")

print("=== VERIFYING EXTRACTED ROSSMANN FILES ===")
df_train = pd.read_csv(train_path, low_memory=False)
df_store = pd.read_csv(store_path)

print(f"train.csv rows: {len(df_train)}, cols: {len(df_train.columns)}")
print(f"store.csv rows: {len(df_store)}, cols: {len(df_store.columns)}")

df_train['Date'] = pd.to_datetime(df_train['Date'])
print(f"Date range: {df_train['Date'].min()} to {df_train['Date'].max()} ({df_train['Date'].nunique()} days)")
print(f"Unique stores in train: {df_train['Store'].nunique()}")
print(f"Unique stores in store: {df_store['Store'].nunique()}")

# Missing values
print("\nMissing values in train.csv:")
print(df_train.isnull().sum())
print("\nMissing values in store.csv:")
print(df_store.isnull().sum())

# Open vs Sales
closed_total = (df_train['Open'] == 0).sum()
closed_zero_sales = ((df_train['Open'] == 0) & (df_train['Sales'] == 0)).sum()
open_total = (df_train['Open'] == 1).sum()
open_zero_sales = ((df_train['Open'] == 1) & (df_train['Sales'] == 0)).sum()

print(f"\nClosed rows: {closed_total}, Closed with Sales==0: {closed_zero_sales} ({closed_zero_sales/closed_total*100:.2f}%)")
print(f"Open rows: {open_total}, Open with Sales==0: {open_zero_sales}")

# Target stats for Open == 1
sales_open = df_train[df_train['Open'] == 1]['Sales']
print("\nSales statistics for Open == 1 stores:")
print(sales_open.describe())
