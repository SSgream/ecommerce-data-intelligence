
CREATE INDEX IF NOT EXISTS idx_forecast_date
ON fact_sales_forecast(date);

CREATE INDEX IF NOT EXISTS idx_forecast_store
ON fact_sales_forecast(store_nbr);

CREATE INDEX IF NOT EXISTS idx_forecast_family
ON fact_sales_forecast(family_id);
