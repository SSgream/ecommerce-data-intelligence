
from pathlib import Path

import pendulum

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


# =========================================================
# PROJECT CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(
    "/mnt/d/04 Porto/ecommerce-data-intelligence"
)

DBT_PROJECT = PROJECT_ROOT / "ecommerce_analytics"

PYTHON_EXECUTABLE = (
    "/home/selwin/.venvs/ecommerce-pipeline/bin/python"
)

DBT_EXECUTABLE = (
    "/home/selwin/.venvs/ecommerce-dbt/bin/dbt"
)


# =========================================================
# VALIDATE PROJECT FILES
# =========================================================

def validate_project_files():

    required_files = [
        PROJECT_ROOT / ".env",

        PROJECT_ROOT / "data/raw/train.csv",
        PROJECT_ROOT / "data/raw/test.csv",
        PROJECT_ROOT / "data/raw/stores.csv",
        PROJECT_ROOT / "data/raw/transactions.csv",
        PROJECT_ROOT / "data/raw/oil.csv",
        PROJECT_ROOT / "data/raw/holidays_events.csv",
        PROJECT_ROOT / "data/raw/store-sales-time-series-forecasting.zip",
        PROJECT_ROOT / "src/ingestion/ingest_dataset.py",

        PROJECT_ROOT / "src/processing/prepare_features.py",
        PROJECT_ROOT / "src/processing/train_forecast.py",
        PROJECT_ROOT / "src/processing/forecast.py",
        PROJECT_ROOT / "src/database/load_forecast.py",

        DBT_PROJECT / "dbt_project.yml",
    ]

    missing_files = [
        str(file)
        for file in required_files
        if not file.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            f"Required files not found: {missing_files}"
        )

    if not Path(PYTHON_EXECUTABLE).exists():
        raise FileNotFoundError(
            f"Python executable not found: {PYTHON_EXECUTABLE}"
        )

    if not Path(DBT_EXECUTABLE).exists():
        raise FileNotFoundError(
            f"dbt executable not found: {DBT_EXECUTABLE}"
        )

    print("Project files validation successful!")


# =========================================================
# PYTHON PIPELINE COMMANDS
# =========================================================

def python_command(script):

    return f"""
set -e

cd "{PROJECT_ROOT}"

"{PYTHON_EXECUTABLE}" "{PROJECT_ROOT / script}"
"""

INGEST_DATASET_COMMAND = python_command(
    "src/ingestion/ingest_dataset.py"
)

PREPARE_FEATURES_COMMAND = python_command(
    "src/processing/prepare_features.py"
)

TRAIN_FORECAST_COMMAND = python_command(
    "src/processing/train_forecast.py"
)

GENERATE_FORECAST_COMMAND = python_command(
    "src/processing/forecast.py"
)

LOAD_FORECAST_COMMAND = python_command(
    "src/database/load_forecast.py"
)


# =========================================================
# DBT COMMANDS
# =========================================================

DBT_RUN_COMMAND = f"""
set -e

cd "{DBT_PROJECT}"

export POSTGRES_PASSWORD="$(grep '^POSTGRES_PASSWORD=' "{PROJECT_ROOT}/.env" | cut -d '=' -f2- | tr -d '\\r')"

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "POSTGRES_PASSWORD is empty"
    exit 1
fi

"{DBT_EXECUTABLE}" run
"""


DBT_TEST_COMMAND = f"""
set -e

cd "{DBT_PROJECT}"

export POSTGRES_PASSWORD="$(grep '^POSTGRES_PASSWORD=' "{PROJECT_ROOT}/.env" | cut -d '=' -f2- | tr -d '\\r')"

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "POSTGRES_PASSWORD is empty"
    exit 1
fi

"{DBT_EXECUTABLE}" test
"""


# =========================================================
# AIRFLOW DAG
# =========================================================

with DAG(
    dag_id="ecommerce_data_pipeline",
    description="End-to-End E-Commerce Data Intelligence Pipeline",

    start_date=pendulum.datetime(
        2026, 11, 18, tz="Asia/Makassar"
    ),

    schedule=None,
    catchup=False,

    tags=[
        "data-engineering",
        "ecommerce",
        "machine-learning",
        "analytics"
    ],

) as dag:

    start = EmptyOperator(
        task_id="start_pipeline"
    )

    validate = PythonOperator(
        task_id="validate_project_files",
        python_callable=validate_project_files,
    )
    
    ingest_dataset = BashOperator(
        task_id="data_ingestion",
        bash_command=INGEST_DATASET_COMMAND,
    )

    prepare_features = BashOperator(
        task_id="prepare_features",
        bash_command=PREPARE_FEATURES_COMMAND,
    )

    train_forecast = BashOperator(
        task_id="train_forecast",
        bash_command=TRAIN_FORECAST_COMMAND,
    )

    generate_forecast = BashOperator(
        task_id="generate_forecast",
        bash_command=GENERATE_FORECAST_COMMAND,
    )

    load_forecast = BashOperator(
        task_id="load_forecast",
        bash_command=LOAD_FORECAST_COMMAND,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=DBT_RUN_COMMAND,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=DBT_TEST_COMMAND,
    )

    finish = EmptyOperator(
        task_id="finish_pipeline"
    )


    # Pipeline dependencies

    (
        start
        >> validate
        >> ingest_dataset
        >> prepare_features
        >> train_forecast
        >> generate_forecast
        >> load_forecast
        >> dbt_run
        >> dbt_test
        >> finish
    )
