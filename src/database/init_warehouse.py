from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

SQL_DIR = PROJECT_ROOT / "warehouse" / "sql"

sql_files = [
    "01_create_dimensions.sql",
    "02_create_fact_tables.sql",
    "03_create_indexes.sql",
]

with engine.begin() as connection:
    for filename in sql_files:
        print(f"Executing: {filename}")
        sql_script = (SQL_DIR / filename).read_text(encoding="utf-8")
        connection.execute(text(sql_script))

print("Data Warehouse initialized successfully!")

engine.dispose()