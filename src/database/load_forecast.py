
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# =========================================================
# PROJECT CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sales_forecast_candidate.csv"
)

load_dotenv(PROJECT_ROOT / ".env", override=True)


# =========================================================
# DATABASE CONNECTION
# =========================================================

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(DATABASE_URL)


# =========================================================
# READ FORECAST DATA
# =========================================================

print("Loading forecast CSV...")

forecast = pd.read_csv(
    DATA_PATH,
    parse_dates=["date"]
)

print("CSV records:", len(forecast))


# =========================================================
# VALIDATE SOURCE DATA
# =========================================================

required_columns = [
    "id",
    "date",
    "store_nbr",
    "family",
    "predicted_sales"
]

for col in required_columns:
    if col not in forecast.columns:
        raise ValueError(f"Missing column: {col}")

if forecast["id"].duplicated().any():
    raise ValueError("Duplicate forecast ID detected.")

if forecast.duplicated(
    ["date", "store_nbr", "family"]
).any():
    raise ValueError("Duplicate forecast grain detected.")

if forecast.isna().any().any():
    raise ValueError("Missing values detected.")

if (forecast["predicted_sales"] < 0).any():
    raise ValueError("Negative forecast detected.")


# =========================================================
# GET FAMILY DIMENSION MAPPING
# =========================================================

with engine.connect() as connection:

    family_mapping = pd.read_sql(
        text("""
            SELECT family_id, family_name
            FROM dim_family
        """),
        connection
    )


# =========================================================
# MAP FAMILY ID
# =========================================================

forecast = forecast.merge(
    family_mapping,
    left_on="family",
    right_on="family_name",
    how="left",
    validate="many_to_one"
)

if forecast["family_id"].isna().any():
    raise ValueError(
        "Some product families are missing in dim_family."
    )


# =========================================================
# PREPARE FACT TABLE DATA
# =========================================================

fact_forecast = forecast[
    [
        "id",
        "date",
        "store_nbr",
        "family_id",
        "predicted_sales"
    ]
].copy()

fact_forecast["date"] = (
    fact_forecast["date"].dt.date
)

fact_forecast["predicted_sales"] = (
    fact_forecast["predicted_sales"].round(2)
)

fact_forecast["id"] = fact_forecast["id"].astype(int)
fact_forecast["store_nbr"] = fact_forecast["store_nbr"].astype(int)
fact_forecast["family_id"] = fact_forecast["family_id"].astype(int)


# =========================================================
# UPSERT INTO POSTGRESQL
# =========================================================

print("\nLoading data into PostgreSQL...")

upsert_sql = text("""
    INSERT INTO fact_sales_forecast (
        id,
        date,
        store_nbr,
        family_id,
        predicted_sales
    )
    VALUES (
        :id,
        :date,
        :store_nbr,
        :family_id,
        :predicted_sales
    )
    ON CONFLICT (id)
    DO UPDATE SET
        date = EXCLUDED.date,
        store_nbr = EXCLUDED.store_nbr,
        family_id = EXCLUDED.family_id,
        predicted_sales = EXCLUDED.predicted_sales,
        created_at = CURRENT_TIMESTAMP
""")

records = fact_forecast.to_dict(orient="records")

with engine.begin() as connection:

    for start in range(0, len(records), 1000):

        batch = records[start:start + 1000]

        connection.execute(
            upsert_sql,
            batch
        )

        print(
            f"Processed {min(start + 1000, len(records))}"
            f"/{len(records)} records"
        )


# =========================================================
# VERIFY DATABASE
# =========================================================

with engine.connect() as connection:

    total_records = connection.execute(
        text("""
            SELECT COUNT(*)
            FROM fact_sales_forecast
        """)
    ).scalar()

    forecast_records = connection.execute(
        text("""
            SELECT COUNT(*)
            FROM fact_sales_forecast
            WHERE date BETWEEN '2017-08-16' AND '2017-08-31'
        """)
    ).scalar()

    forecast_total = connection.execute(
        text("""
            SELECT ROUND(SUM(predicted_sales)::numeric, 2)
            FROM fact_sales_forecast
            WHERE date BETWEEN '2017-08-16' AND '2017-08-31'
        """)
    ).scalar()


# =========================================================
# SUMMARY
# =========================================================

print("\nFORECAST LOADING COMPLETED")
print("=" * 45)

print("CSV records:", len(fact_forecast))
print("Records in PostgreSQL:", total_records)
print("Forecast records in PostgreSQL:", forecast_records)
print("Forecast total sales:", forecast_total)

engine.dispose()
