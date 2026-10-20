
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.sql_validator import validate_sql


valid_queries = [
    "SELECT * FROM products",
    "SELECT category, COUNT(*) FROM products GROUP BY category;",
]

invalid_queries = [
    "DELETE FROM products",
    "DROP TABLE products",
    "SELECT * FROM products; DROP TABLE products",
    "SELECT * FROM products -- comment",
    "PRAGMA table_info(products)",
]

for query in valid_queries:
    validate_sql(query)
    print("PASS: Valid query accepted")

for query in invalid_queries:
    try:
        validate_sql(query)
        print("FAIL: Unsafe query accepted:", query)
    except ValueError:
        print("PASS: Unsafe query rejected")
