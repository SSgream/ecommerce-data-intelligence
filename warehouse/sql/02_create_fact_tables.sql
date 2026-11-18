
CREATE TABLE IF NOT EXISTS fact_sales_forecast (
    id BIGINT PRIMARY KEY,
    date DATE NOT NULL,
    store_nbr INTEGER NOT NULL,
    family_id INTEGER NOT NULL,
    predicted_sales NUMERIC(14, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_forecast_date
        FOREIGN KEY (date)
        REFERENCES dim_date(date),

    CONSTRAINT fk_forecast_store
        FOREIGN KEY (store_nbr)
        REFERENCES dim_store(store_nbr),

    CONSTRAINT fk_forecast_family
        FOREIGN KEY (family_id)
        REFERENCES dim_family(family_id),

    CONSTRAINT uq_forecast_grain
        UNIQUE (date, store_nbr, family_id)
);
