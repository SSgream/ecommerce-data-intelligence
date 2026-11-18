
CREATE TABLE IF NOT EXISTS fact_sales_streaming (
    run_id UUID NOT NULL,
    family_name VARCHAR(100) NOT NULL,
    total_transactions BIGINT NOT NULL DEFAULT 0,
    total_sales NUMERIC(18, 3) NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (run_id, family_name)
);
