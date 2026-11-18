
-- 1. Total prediksi penjualan per hari
CREATE OR REPLACE VIEW vw_daily_forecast AS
SELECT
    d.date,
    d.year,
    d.month,
    d.day,
    SUM(f.predicted_sales) AS total_predicted_sales,
    COUNT(*) AS total_records,
    AVG(f.predicted_sales) AS avg_predicted_sales
FROM fact_sales_forecast f
JOIN dim_date d ON f.date = d.date
GROUP BY d.date, d.year, d.month, d.day;


-- 2. Prediksi penjualan per kategori produk
CREATE OR REPLACE VIEW vw_family_forecast AS
SELECT
    df.family_name,
    SUM(f.predicted_sales) AS total_predicted_sales,
    COUNT(*) AS total_records,
    AVG(f.predicted_sales) AS avg_predicted_sales
FROM fact_sales_forecast f
JOIN dim_family df ON f.family_id = df.family_id
GROUP BY df.family_name;


-- 3. Prediksi penjualan per toko
CREATE OR REPLACE VIEW vw_store_forecast AS
SELECT
    ds.store_nbr,
    ds.city,
    ds.state,
    ds.store_type,
    ds.cluster,
    SUM(f.predicted_sales) AS total_predicted_sales,
    COUNT(*) AS total_records,
    AVG(f.predicted_sales) AS avg_predicted_sales
FROM fact_sales_forecast f
JOIN dim_store ds ON f.store_nbr = ds.store_nbr
GROUP BY
    ds.store_nbr,
    ds.city,
    ds.state,
    ds.store_type,
    ds.cluster;


-- 4. Top 10 toko berdasarkan prediksi penjualan
CREATE OR REPLACE VIEW vw_top10_stores AS
SELECT
    store_nbr,
    city,
    state,
    total_predicted_sales,
    total_records
FROM vw_store_forecast
ORDER BY total_predicted_sales DESC
LIMIT 10;


-- 5. Prediksi penjualan per kota
CREATE OR REPLACE VIEW vw_city_forecast AS
SELECT
    ds.city,
    ds.state,
    SUM(f.predicted_sales) AS total_predicted_sales,
    COUNT(DISTINCT ds.store_nbr) AS total_stores,
    COUNT(*) AS total_records,
    AVG(f.predicted_sales) AS avg_predicted_sales
FROM fact_sales_forecast f
JOIN dim_store ds ON f.store_nbr = ds.store_nbr
GROUP BY ds.city, ds.state;
