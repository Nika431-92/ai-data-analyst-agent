
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "analytics.db"

connection = sqlite3.connect(DB_PATH)

query = """
SELECT
    p.category,
    COUNT(o.order_id) AS total_orders,
    SUM(o.quantity * p.price) AS total_revenue
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
WHERE o.status = 'delivered'
GROUP BY p.category
ORDER BY total_revenue DESC;
"""

cursor = connection.execute(query)
results = cursor.fetchall()

print("\nSALES ANALYSIS REPORT")
print("-" * 50)

for category, total_orders, revenue in results:
    print(
        f"Category: {category} | "
        f"Orders: {total_orders} | "
        f"Revenue: Rs.{revenue:,}"
    )

connection.close()
