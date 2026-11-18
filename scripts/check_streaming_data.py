
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=True)

with psycopg.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5435")),
    dbname=os.getenv("POSTGRES_DB", "ecommerce_dw"),
    user=os.getenv("POSTGRES_USER", "ecommerce_user"),
    password=os.getenv("POSTGRES_PASSWORD")
) as conn:

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                family_name,
                total_transactions,
                total_sales,
                updated_at
            FROM fact_sales_streaming
            ORDER BY total_sales DESC;
        """)

        rows = cursor.fetchall()

        print("\nPOSTGRESQL STREAMING VALIDATION")
        print("=" * 75)

        for row in rows:
            print(
                f"{row[0]:30} | "
                f"{row[1]:5} transactions | "
                f"Sales: {row[2]}"
            )

        print("=" * 75)
        print(f"Total Families: {len(rows)}")
