
import csv
import random
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

products = [
    (101, "Wireless Mouse", "Electronics", 799),
    (102, "Mechanical Keyboard", "Electronics", 2499),
    (103, "Water Bottle", "Home", 399),
    (104, "Desk Lamp", "Home", 1299),
    (105, "Running Shoes", "Fashion", 2999),
    (106, "Backpack", "Fashion", 1599),
    (107, "Python Basics", "Books", 599),
    (108, "Data Science Guide", "Books", 899),
]

with open(DATA_DIR / "products.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["product_id", "product_name", "category", "price"])
    writer.writerows(products)

with open(DATA_DIR / "orders.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "order_id", "customer_id", "product_id",
        "quantity", "order_date", "status"
    ])

    for order_id in range(1, 101):
        product = random.choice(products)
        customer_id = random.randint(1001, 1030)
        quantity = random.randint(1, 3)
        day = random.randint(1, 28)

        status = random.choices(
            ["delivered", "cancelled", "returned"],
            weights=[85, 10, 5],
            k=1
        )[0]

        writer.writerow([
            order_id,
            customer_id,
            product[0],
            quantity,
            f"2026-09-{day:02d}",
            status
        ])

print("Sample dataset created successfully!")
print(f"Products: {DATA_DIR / 'products.csv'}")
print(f"Orders:   {DATA_DIR / 'orders.csv'}")
