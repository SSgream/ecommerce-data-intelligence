
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=True)

conn = psycopg.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

queries = {
    "mart_sales_by_store": """
        SELECT
            COUNT(*) AS total_rows,
            SUM(total_forecasts) AS total_forecasts,
            ROUND(SUM(total_predicted_sales), 2) AS total_sales
        FROM mart_sales_by_store
    """,
    "mart_sales_by_family": """
        SELECT
            COUNT(*) AS total_rows,
            SUM(total_forecasts) AS total_forecasts,
            ROUND(SUM(total_predicted_sales), 2) AS total_sales
        FROM mart_sales_by_family
    """,
    "mart_daily_sales": """
        SELECT
            COUNT(*) AS total_rows,
            SUM(total_forecasts) AS total_forecasts,
            ROUND(SUM(total_predicted_sales), 2) AS total_sales
        FROM mart_daily_sales
    """
}

try:
    with conn.cursor() as cur:
        print("=" * 65)
        print("DBT DATA MART VALIDATION")
        print("=" * 65)

        for mart, query in queries.items():
            cur.execute(query)
            result = cur.fetchone()

            print(f"\n{mart}")
            print("-" * 45)
            print(f"Total Rows       : {result[0]:,}")
            print(f"Total Forecasts  : {result[1]:,}")
            print(f"Total Sales      : {result[2]:,.2f}")

finally:
    conn.close()
