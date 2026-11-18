
CREATE TABLE IF NOT EXISTS dim_store (
    store_nbr INTEGER PRIMARY KEY,
    city VARCHAR(100),
    state VARCHAR(100),
    store_type VARCHAR(10),
    cluster INTEGER
);

CREATE TABLE IF NOT EXISTS dim_date (
    date DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    week_of_year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_family (
    family_id SERIAL PRIMARY KEY,
    family_name VARCHAR(100) UNIQUE NOT NULL
);
