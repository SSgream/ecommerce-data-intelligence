
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Project configuration
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

load_dotenv(PROJECT_ROOT / ".env", override=True)

# PostgreSQL connection
DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(DATABASE_URL)

# Load source datasets
stores = pd.read_csv(DATA_DIR / "stores.csv")
train = pd.read_csv(DATA_DIR / "train.csv", usecols=["date", "family"])
test = pd.read_csv(DATA_DIR / "test.csv", usecols=["date", "family"])

# =========================================
# 1. DIM_STORE
# =========================================
dim_store = stores.rename(
    columns={"type": "store_type"}
)

dim_store.to_sql(
    "dim_store",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=500
)

# =========================================
# 2. DIM_FAMILY
# =========================================
dim_family = pd.DataFrame({
    "family_name": sorted(train["family"].unique())
})

dim_family.to_sql(
    "dim_family",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=500
)

# =========================================
# 3. DIM_DATE
# =========================================
all_dates = pd.concat(
    [train["date"], test["date"]],
    ignore_index=True
)

dates = pd.date_range(
    start=pd.to_datetime(all_dates).min(),
    end=pd.to_datetime(all_dates).max(),
    freq="D"
)

dim_date = pd.DataFrame({"date": dates})

dim_date["year"] = dim_date["date"].dt.year
dim_date["month"] = dim_date["date"].dt.month
dim_date["day"] = dim_date["date"].dt.day
dim_date["day_of_week"] = dim_date["date"].dt.dayofweek
dim_date["day_of_year"] = dim_date["date"].dt.dayofyear
dim_date["week_of_year"] = (
    dim_date["date"].dt.isocalendar().week.astype(int)
)
dim_date["quarter"] = dim_date["date"].dt.quarter
dim_date["is_weekend"] = (
    dim_date["day_of_week"] >= 5
)

dim_date["date"] = dim_date["date"].dt.date

dim_date.to_sql(
    "dim_date",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000
)

# =========================================
# VERIFICATION
# =========================================
with engine.connect() as connection:
    for table in ["dim_store", "dim_family", "dim_date"]:
        result = connection.exec_driver_sql(
            f"SELECT COUNT(*) FROM {table}"
        )
        print(f"{table}: {result.scalar()} records")

engine.dispose()

print("\nDimension loading completed successfully!")
