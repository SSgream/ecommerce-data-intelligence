
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

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

SQL_PATH = (
    PROJECT_ROOT
    / "warehouse"
    / "sql"
    / "04_analytical_queries.sql"
)

sql_script = SQL_PATH.read_text(encoding="utf-8")
sql_statements = [
    statement.strip()
    for statement in sql_script.split(";")
    if statement.strip()
]

with engine.begin() as connection:
    for statement in sql_statements:
        connection.exec_driver_sql(statement)
        print("View berhasil dibuat.")

engine.dispose()

print("\nAnalytical views created successfully!")
