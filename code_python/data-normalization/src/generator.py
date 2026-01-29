import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

def generate_raw_data(
    output_path: str,
    num_records: int = 100,
    num_customers: int = 20,
    num_products: int = 10
):
    """
    Generates a denormalized CSV file simulating raw sales data.
    """

    # Pre-define a pool of customers
    customers = []
    for i in range(num_customers):
        customers.append({
            "name": f"Customer_{i}",
            "email": f"customer_{i}@example.com"
        })

    # Pre-define a pool of products
    products = []
    categories = ["Electronics", "Books", "Home", "Clothing"]
    for i in range(num_products):
        products.append({
            "name": f"Product_{i}",
            "category": random.choice(categories),
            "price": round(random.uniform(10.0, 500.0), 2)
        })

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    headers = [
        "transaction_id",
        "customer_name",
        "customer_email",
        "product_name",
        "category",
        "unit_price",
        "quantity",
        "timestamp"
    ]

    print(f"Generating {num_records} records to {output_path}...")

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for _ in range(num_records):
            customer = random.choice(customers)
            product = random.choice(products)

            # Simulate date within last 30 days
            days_offset = random.randint(0, 30)
            date = datetime.now() - timedelta(days=days_offset)

            record = {
                "transaction_id": str(uuid.uuid4()),
                "customer_name": customer["name"],
                "customer_email": customer["email"],
                "product_name": product["name"],
                "category": product["category"],
                "unit_price": product["price"],
                "quantity": random.randint(1, 5),
                "timestamp": date.isoformat()
            }

            writer.writerow(record)

    print("Done.")

if __name__ == "__main__":
    generate_raw_data("code_python/data-normalization/data/raw_data.csv")
