
import re
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "analytics.db"


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "REPLACE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "VACUUM",
    "REINDEX",
}


def validate_sql(sql: str) -> str:
    if not sql or not sql.strip():
        raise ValueError("SQL query cannot be empty.")

    query = sql.strip().rstrip(";").strip()

    if not re.match(r"(?is)^SELECT\b", query):
        raise ValueError("Only SELECT queries are allowed.")

    if "--" in query or "/*" in query or "*/" in query:
        raise ValueError("SQL comments are not allowed.")

    keywords = re.findall(r"\b[A-Za-z_]+\b", query)
    for keyword in keywords:
        if keyword.upper() in FORBIDDEN_KEYWORDS:
            raise ValueError(
                f"Forbidden SQL keyword: {keyword.upper()}"
            )

    # Check the query against the real database schema.
    connection = sqlite3.connect(
        f"file:{DB_PATH.as_posix()}?mode=ro",
        uri=True,
    )

    try:
        connection.execute("EXPLAIN " + query)
    except sqlite3.Error as error:
        raise ValueError(f"Invalid SQL query: {error}") from error
    finally:
        connection.close()

    return query
