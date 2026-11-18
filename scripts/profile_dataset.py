
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw")
CHUNK_SIZE = 200_000

print("=" * 60)
print("DATASET PROFILING")
print("=" * 60)

# 1. Profiling train.csv menggunakan chunks
total_rows = 0
missing_values = {}
min_date = None
max_date = None
sales_sum = 0
sales_min = float("inf")
sales_max = float("-inf")
promotion_sum = 0

for chunk in pd.read_csv(
    DATA_DIR / "train.csv",
    chunksize=CHUNK_SIZE
):
    total_rows += len(chunk)

    for column, count in chunk.isna().sum().items():
        missing_values[column] = (
            missing_values.get(column, 0) + count
        )

    chunk_min = pd.to_datetime(chunk["date"]).min()
    chunk_max = pd.to_datetime(chunk["date"]).max()

    min_date = chunk_min if min_date is None else min(min_date, chunk_min)
    max_date = chunk_max if max_date is None else max(max_date, chunk_max)

    sales_sum += chunk["sales"].sum()
    sales_min = min(sales_min, chunk["sales"].min())
    sales_max = max(sales_max, chunk["sales"].max())

    promotion_sum += chunk["onpromotion"].sum()

print("\n[TRAIN DATA]")
print("Total rows:", f"{total_rows:,}")
print("Date range:", min_date, "to", max_date)
print("Total sales:", round(sales_sum, 2))
print("Minimum sales:", sales_min)
print("Maximum sales:", sales_max)
print("Total promotions:", f"{promotion_sum:,}")

print("\nMissing values:")
for column, count in missing_values.items():
    print(f"{column}: {count:,}")

# 2. Profiling dataset pendukung
print("\n" + "=" * 60)
print("SUPPORTING DATASETS")
print("=" * 60)

for filename in [
    "test.csv",
    "stores.csv",
    "transactions.csv",
    "oil.csv",
    "holidays_events.csv"
]:
    df = pd.read_csv(DATA_DIR / filename)

    print(f"\n{filename}")
    print("Rows:", f"{len(df):,}")
    print("Columns:", list(df.columns))
    print("Missing values:")
    print(df.isna().sum().to_dict())

# 3. Jumlah toko dan kategori produk
print("\n" + "=" * 60)
print("DIMENSION SUMMARY")
print("=" * 60)

stores = pd.read_csv(DATA_DIR / "stores.csv")
print("Total stores:", stores["store_nbr"].nunique())

families = set()
dates = set()

for chunk in pd.read_csv(
    DATA_DIR / "train.csv",
    chunksize=CHUNK_SIZE,
    usecols=["family"]
):
    families.update(chunk["family"].dropna().unique())

print("Total product families:", len(families))
print("Product families:", sorted(families))

print("\nProfiling completed.")
