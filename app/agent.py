
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# --------------------------------------------------
# 1. Project configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-3.5-flash-lite"

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found. Check your root .env file."
    )

client = genai.Client(api_key=API_KEY)

from app.sql_validator import validate_sql
from scripts.query_engine import run_query


# --------------------------------------------------
# 2. Database schema for Gemini
# --------------------------------------------------

SCHEMA = """
Database: SQLite

Table: products
- product_id: integer
- product_name: text
- category: text
- price: real

Table: orders
- order_id: integer
- customer_id: integer
- product_id: integer
- quantity: integer
- order_date: text (YYYY-MM-DD)
- status: text (delivered, cancelled, returned)

Relationship:
orders.product_id = products.product_id

Revenue calculation:
quantity * price

Delivered revenue:
Filter orders using status = 'delivered'.
"""


# --------------------------------------------------
# 3. Generate SQL using Gemini
# --------------------------------------------------

def generate_sql(question: str) -> str:
    prompt = f"""
You are an expert data analyst who generates SQLite queries.

DATABASE SCHEMA:
{SCHEMA}

USER QUESTION:
{question}

RULES:
1. Return exactly one read-only SELECT query.
2. Use only the tables and columns in the schema.
3. Never modify the database.
4. Do not include SQL comments or Markdown code fences.
5. For the five most expensive products, select product_name,
   category and price from products, order by price DESC,
   and limit the results to 5.
6. For highest revenue, calculate delivered revenue using
   quantity * price and join orders with products.
7. For total orders, count rows in orders.
8. For cancelled orders, filter status = 'cancelled'.
9. Use LIMIT 100 for detail queries unless the question
   explicitly asks for a smaller number of results.
10. Return only the SQL query.
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            sql = response.text.strip()

            # Remove Markdown fences if the model adds them.
            sql = re.sub(
                r"^\s*```(?:sql)?\s*|\s*```\s*$",
                "",
                sql,
                flags=re.IGNORECASE,
            ).strip()

            return sql

        except Exception as error:
            error_text = str(error)

            is_temporary = (
                "503" in error_text
                or "UNAVAILABLE" in error_text.upper()
            )

            if not is_temporary:
                raise

            if attempt == 2:
                raise

            wait_seconds = 2 ** (attempt + 1)

            print(
                f"Gemini is temporarily unavailable. "
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError("Unable to generate SQL.")


# --------------------------------------------------
# 4. Answer a natural-language question
# --------------------------------------------------


def answer_question(question: str):
    if not question.strip():
        print("Please enter a question.")
        return

    print("\nGenerating SQL with Gemini...")

    sql = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql)


    # Validate before executing.
    safe_sql = validate_sql(sql)

    # Execute through the existing read-only query engine.
    result = run_query(safe_sql)

    print("\nAnalysis Results")
    print("-" * 60)

    if not result["rows"]:
        print("No results found.")
        return

    print(" | ".join(str(column) for column in result["columns"]))
    print("-" * 60)

    for row in result["rows"]:
        print(" | ".join(str(value) for value in row))

    print("-" * 60)
    print(f"Rows returned: {len(result['rows'])}")


# --------------------------------------------------
# 5. Interactive application
# --------------------------------------------------

def main():
    print("=" * 50)
    print("       AI DATA ANALYST AGENT")
    print("=" * 50)
    print("Ask questions about products, orders, and revenue.")
    print("Type 'exit' to quit.")

    while True:
        try:
            question = input("\nYour question: ").strip()

            if question.lower() == "exit":
                print("Goodbye, buddy!")
                break

            if not question:
                continue

            answer_question(question)

        except KeyboardInterrupt:
            print("\nAgent stopped.")
            break

        except Exception as error:
            print(f"\nCould not answer the question: {error}")
            print("Check the error and try again.")


if __name__ == "__main__":
    main()
