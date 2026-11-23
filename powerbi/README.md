# Power BI Dashboard – E-Commerce Data Intelligence Platform

## Overview

The Power BI dashboard is the Business Intelligence and Data Visualization layer of the E-Commerce Data Intelligence Platform. It transforms sales forecasting results stored in PostgreSQL into interactive dashboards, providing insights into overall sales performance, store performance, and product family performance.

The dashboard is designed to help users explore forecasted sales trends, compare business performance, and identify the highest- and lowest-performing stores and product families.

## Dashboard Structure

The dashboard consists of three interactive analytical sections:

### 1. Sales Overview

Provides a high-level summary of the sales forecasting results.

**Key Metrics:**
- Total Predicted Sales
- Total Forecast Records
- Total Stores
- Total Product Families
- Daily Predicted Sales Trend
- Daily Average Predicted Sales
- Forecast Records by Date
- Top Store
- Lowest Store
- Top Product Family
- Lowest Product Family
- Forecast Window

### 2. Store Analysis

Focuses on analyzing forecasted sales performance across different store locations.

**Analysis Includes:**
- Store-level predicted sales
- Store performance comparison
- Top-performing stores
- Lowest-performing stores
- Sales distribution by city
- Store characteristics and geographical dimensions

### 3. Product Analysis

Provides insights into predicted sales performance across product families.

**Analysis Includes:**
- Predicted sales by product family
- Product family performance comparison
- Top-performing product family
- Lowest-performing product family
- Average, maximum, and minimum predicted sales
- Product family contribution to total predicted sales

## Data Sources

The dashboard connects directly to the PostgreSQL data warehouse and uses analytical tables generated through dbt.

| Data Source | Description |
|---|---|
| `mart_daily_sales` | Daily sales forecasting summaries |
| `mart_sales_by_store` | Forecasted sales aggregated by store |
| `mart_sales_by_family` | Forecasted sales aggregated by product family |

These analytical marts provide structured and aggregated data for dashboard reporting, reducing the need for additional transformations inside Power BI.

## Data Pipeline Integration

The Power BI dashboard is the final visualization layer of the data engineering pipeline.

```text
Kaggle Dataset
      |
      v
Data Processing & Feature Engineering
      |
      v
XGBoost Forecasting Model
      |
      v
Forecast Results
      |
      v
PostgreSQL Data Warehouse
      |
      v
dbt Transformation
      |
      v
Analytical Data Marts
      |
      v
Power BI Dashboard
```

## Technologies Used

- **Microsoft Power BI** – Interactive dashboards and data visualization.
- **PostgreSQL** – Data warehouse and analytical data storage.
- **dbt** – Data transformation and analytical modeling.
- **Python** – Data processing and forecasting.
- **XGBoost** – Sales forecasting model.
- **Docker** – Containerized PostgreSQL environment.

## Key Features

- Interactive dashboard navigation across three analytical sections.
- KPI cards for monitoring forecast performance.
- Dynamic reporting periods based on available forecast dates.
- Top and bottom performance identification for stores and product families.
- Daily sales trend visualization.
- Store and product family performance comparisons.
- Dynamic DAX measures that respond to report filters.
- PostgreSQL integration for accessing warehouse data.

## Database Connection

The dashboard connects to PostgreSQL using the following configuration:

| Parameter | Value |
|---|---|
| Server | `localhost:5435` |
| Database | `ecommerce_dw` |
| Schema | `public` |
| Data Source | PostgreSQL |
| Connectivity Mode | Import |

**Note:** Database credentials are configured locally and should not be committed to the public repository.

## Data Refresh

The dashboard uses Power BI Import Mode.

To retrieve updated forecasting results:

1. Start Docker Desktop.
2. Start the PostgreSQL container.
3. Ensure the PostgreSQL database is accessible.
4. Open the Power BI project.
5. Select **Home → Refresh**.

The dashboard measures and reporting period will update based on the refreshed data.

Previously imported data can still be viewed in Power BI without the PostgreSQL container running. However, a database connection is required to refresh the dataset.

## Forecast Dataset

The current forecasting results cover:

| Metric | Value |
|---|---:|
| Forecast Period | August 16–31, 2017 |
| Forecast Duration | 16 Days |
| Forecast Records | 28,512 |
| Stores | 54 |
| Product Families | 33 |
| Total Predicted Sales | 12,868,054.18 |

## Project Repository

The Power BI dashboard is part of the larger E-Commerce Data Intelligence Platform.

**GitHub Repository:**  
https://github.com/SSgream/ecommerce-data-intelligence

## Purpose

This dashboard demonstrates the integration of data engineering, predictive analytics, data warehousing, and business intelligence into an end-to-end analytical solution.

It transforms machine learning forecasting outputs into interactive business insights that support sales monitoring, store performance evaluation, and product-level analysis.
