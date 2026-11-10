CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    order_date DATE NOT NULL,
    region TEXT NOT NULL,
    product_category TEXT NOT NULL,
    customer_segment TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    revenue NUMERIC(12,2) NOT NULL CHECK (revenue >= 0)
);
COPY orders FROM '/seed/orders.csv' WITH (FORMAT csv, HEADER true);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_region ON orders(region);
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analyst_reader') THEN
        CREATE ROLE analyst_reader LOGIN PASSWORD 'reader-local-only';
    END IF;
END
$$;
GRANT CONNECT ON DATABASE analyst TO analyst_reader;
GRANT USAGE ON SCHEMA public TO analyst_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_reader;
