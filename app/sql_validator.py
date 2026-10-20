
import re


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

    query = sql.strip()

    # Allow only one SQL statement.
    if ";" in query.rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed.")

    # Remove one optional trailing semicolon.
    query = query.rstrip(";").strip()

    if not re.match(r"(?is)^SELECT\b", query):
        raise ValueError("Only SELECT queries are allowed.")

    # Block SQL comments to reduce opportunities for bypasses.
    if "--" in query or "/*" in query or "*/" in query:
        raise ValueError("SQL comments are not allowed.")

    # Block forbidden SQL keywords.
    keywords = re.findall(r"\b[A-Za-z_]+\b", query)
    for keyword in keywords:
        if keyword.upper() in FORBIDDEN_KEYWORDS:
            raise ValueError(
                f"Forbidden SQL keyword: {keyword.upper()}"
            )

    return query
