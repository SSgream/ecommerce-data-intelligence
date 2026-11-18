
# E-Commerce Data Intelligence Platform

An end-to-end Data Engineering and Machine Learning project for grocery sales forecasting, streaming data processing, and analytical data warehousing.

## Project Overview

This project implements an end-to-end data platform using the Corporación Favorita Grocery Sales Forecasting dataset from Kaggle.

The platform integrates batch data processing, streaming ingestion, machine learning forecasting, dimensional data warehousing, analytical transformations, and workflow orchestration.

## Technology Stack

| Category | Technology |
|---|---|
| Programming | Python |
| Data Ingestion | Apache Kafka |
| Stream Processing | Apache Spark |
| Data Processing | Pandas, NumPy |
| Machine Learning | XGBoost, Scikit-learn |
| Data Warehouse | PostgreSQL |
| Data Transformation | dbt |
| Workflow Orchestration | Apache Airflow |
| Containerization | Docker |
| Development | VS Code, WSL2 |

## Architecture

The platform consists of two main pipelines:

**1. Batch Forecasting Pipeline**

Kaggle Dataset → Feature Engineering → XGBoost Training → Recursive Forecasting → PostgreSQL → dbt → Analytical Data Marts

**2. Streaming Pipeline**

Sales Dataset → Kafka Producer → Apache Kafka → Spark Structured Streaming → PostgreSQL

For the detailed architecture, see [System Architecture](docs/architecture.md).

## Key Features

- Historical sales data exploration and profiling.
- Feature engineering with lag and rolling-window features.
- XGBoost-based sales forecasting.
- Recursive multi-step forecasting.
- Kafka-based streaming ingestion.
- Spark Structured Streaming and aggregation.
- PostgreSQL dimensional data warehouse.
- dbt staging models and analytical data marts.
- Airflow orchestration for the batch forecasting pipeline.
- Data quality validation and dbt tests.

## Forecasting Results

The forecasting pipeline generates:

| Metric | Result |
|---|---:|
| Forecast Records | 28,512 |
| Stores | 54 |
| Product Families | 33 |
| Forecast Dates | 16 |
| Forecast Period | August 16–31, 2017 |
| Total Predicted Sales | 12,868,054.18 |

The forecast results are loaded into PostgreSQL and transformed into three analytical data marts:

- `mart_sales_by_store`
- `mart_sales_by_family`
- `mart_daily_sales`

All three data marts contain 28,512 underlying forecast records and produce a consistent total predicted sales value.

## Data Warehouse

The PostgreSQL warehouse uses dimensional modeling with:

**Dimensions**
- `dim_store`
- `dim_date`
- `dim_family`

**Fact**
- `fact_sales_forecast`

The streaming pipeline stores its aggregation results separately.

## Project Structure

```text
ecommerce-data-intelligence/
├── dags/
├── data/
│   ├── raw/
│   ├── staging/
│   └── processed/
├── data_science/
│   ├── notebooks/
│   └── models/
├── docs/
│   └── architecture.md
├── ecommerce_analytics/
│   └── models/
│       ├── staging/
│       └── marts/
├── scripts/
├── src/
│   ├── database/
│   ├── ingestion/
│   └── processing/
├── warehouse/
│   └── sql/
├── docker-compose.yml
├── docker-compose.kafka.yml
├── requirements.txt
├── requirements-dbt.txt
└── README.md
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/SSgream/ecommerce-data-intelligence.git
cd ecommerce-data-intelligence
```

### 2. Create a Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For dbt:

```bash
pip install -r requirements-dbt.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Configure the required Kaggle and PostgreSQL credentials in `.env`.

### 5. Start PostgreSQL

```bash
docker compose up -d
```

### 6. Start Kafka

```bash
docker compose -f docker-compose.kafka.yml up -d
```

### 7. Run the Data Pipeline

The batch forecasting pipeline is orchestrated using Apache Airflow.

The DAG executes:

1. Project file validation.
2. Feature preparation.
3. Model training.
4. Recursive forecasting.
5. Forecast loading into PostgreSQL.
6. dbt transformations.
7. dbt data quality tests.

The Kafka and Spark streaming pipeline is executed separately.

## Data Source

Dataset: [Corporación Favorita Grocery Sales Forecasting](https://www.kaggle.com/competitions/store-sales-time-series-forecasting)

The dataset is provided by Kaggle and is subject to its original terms and conditions.

## Documentation

- [System Architecture](docs/architecture.md)

## Project Status

**Completed core pipeline implementation.**

Batch forecasting, Kafka ingestion, Spark stream processing, PostgreSQL warehouse loading, dbt transformations, and Airflow orchestration have been successfully executed and validated.

## Author

Selwin

Data Engineering | Machine Learning | Analytics
