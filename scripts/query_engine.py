
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.sql_validator import validate_sql

DB_PATH = BASE_DIR / "data" / "analytics.db"


def run_query(sql: str):
    # Validate the query before execution.
    safe_sql = validate_sql(sql)

    # Open the database in read-only mode.
    connection = sqlite3.connect(
        f"file:{DB_PATH.as_posix()}?mode=ro",
        uri=True,
    )

    try:
        connection.execute("PRAGMA query_only = ON")
        cursor = connection.execute(safe_sql)

        columns = [item[0] for item in cursor.description]
        rows = cursor.fetchmany(100)

        return {
            "columns": columns,
            "rows": rows,
        }
    finally:
        connection.close()


if __name__ == "__main__":
    result = run_query(
        "SELECT category, COUNT(*) AS product_count "
        "FROM products GROUP BY category"
    )

    print("Columns:", result["columns"])
    for row in result["rows"]:
        print(row)
