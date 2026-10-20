
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.sql_validator import validate_sql


valid_queries = [
    "SELECT * FROM products",
    "SELECT category, COUNT(*) FROM products GROUP BY category;",
    "SELECT category, AVG(price) FROM products GROUP BY category",
    "SELECT * FROM orders WHERE status = 'delivered'",
]

invalid_queries = [
    "",
    "   ",
    "DELETE FROM products",
    "DROP TABLE products",
    "UPDATE products SET price = 0",
    "INSERT INTO products VALUES (109, 'Test', 'Books', 100)",
    "SELECT * FROM products; DROP TABLE products",
    "SELECT * FROM products -- comment",
    "SELECT * FROM products /* comment */",
    "PRAGMA table_info(products)",
    "CREATE TABLE test (id INTEGER)",
    "ATTACH DATABASE 'other.db' AS other",
    "SELECT * FROM products; SELECT * FROM orders",
    "WITH data AS (SELECT 1) SELECT * FROM data",
]


passed = 0
failed = 0

for query in valid_queries:
    try:
        validate_sql(query)
        print("PASS: Valid query accepted")
        passed += 1
    except ValueError as error:
        print("FAIL: Valid query rejected:", query, "|", error)
        failed += 1

for query in invalid_queries:
    try:
        validate_sql(query)
        print("FAIL: Unsafe query accepted:", repr(query))
        failed += 1
    except ValueError:
        print("PASS: Invalid query rejected")
        passed += 1

print(f"\nResults: {passed} passed, {failed} failed")
