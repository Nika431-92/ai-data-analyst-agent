
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "analytics.db"

products = pd.read_csv(DATA_DIR / "products.csv")
orders = pd.read_csv(DATA_DIR / "orders.csv")

with sqlite3.connect(DB_PATH) as connection:
    products.to_sql("products", connection, if_exists="replace", index=False)
    orders.to_sql("orders", connection, if_exists="replace", index=False)

print("SQLite database created successfully!")
print(f"Database: {DB_PATH}")
print(f"Products table: {len(products)} rows")
print(f"Orders table: {len(orders)} rows")
