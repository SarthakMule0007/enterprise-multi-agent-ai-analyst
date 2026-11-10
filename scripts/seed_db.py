"""Seed orders.csv into the configured PostgreSQL database."""
import csv
from pathlib import Path
from sqlalchemy import text
from app.analytics.database import get_engine

ROOT = Path(__file__).resolve().parents[1]


def main():
    rows = list(csv.DictReader((ROOT / "data" / "orders.csv").open(encoding="utf-8")))
    with get_engine().begin() as conn:
        conn.execute(text("""CREATE TABLE IF NOT EXISTS orders (
          order_id INTEGER PRIMARY KEY, order_date DATE NOT NULL, region TEXT NOT NULL,
          product_category TEXT NOT NULL, customer_segment TEXT NOT NULL,
          quantity INTEGER NOT NULL, revenue NUMERIC(12,2) NOT NULL)"""))
        conn.execute(text("DELETE FROM orders"))
        conn.execute(text("""INSERT INTO orders (order_id, order_date, region, product_category,
          customer_segment, quantity, revenue) VALUES (:order_id, :order_date, :region,
          :product_category, :customer_segment, :quantity, :revenue)"""), rows)
    print(f"Seeded {len(rows)} orders")


if __name__ == "__main__":
    main()
