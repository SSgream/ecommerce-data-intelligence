
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=True)

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(DATABASE_URL)

queries = {
    "Total Forecast": """
        SELECT COUNT(*) FROM fact_sales_forecast
    """,
    "Total Stores": """
        SELECT COUNT(*) FROM dim_store
    """,
    "Total Families": """
        SELECT COUNT(*) FROM dim_family
    """,
    "Total Dates": """
        SELECT COUNT(*) FROM dim_date
    """,
    "Total Predicted Sales": """
        SELECT ROUND(SUM(predicted_sales), 2)
        FROM fact_sales_forecast
    """,
    "Average Predicted Sales": """
        SELECT ROUND(AVG(predicted_sales), 2)
        FROM fact_sales_forecast
    """,
    "Missing Store References": """
        SELECT COUNT(*)
        FROM fact_sales_forecast f
        LEFT JOIN dim_store d
            ON f.store_nbr = d.store_nbr
        WHERE d.store_nbr IS NULL
    """,
    "Missing Family References": """
        SELECT COUNT(*)
        FROM fact_sales_forecast f
        LEFT JOIN dim_family d
            ON f.family_id = d.family_id
        WHERE d.family_id IS NULL
    """
}

with engine.connect() as connection:
    print("=" * 45)
    print("DATA WAREHOUSE VALIDATION")
    print("=" * 45)

    for label, query in queries.items():
        result = connection.execute(text(query)).scalar()
        print(f"{label}: {result}")

engine.dispose()
