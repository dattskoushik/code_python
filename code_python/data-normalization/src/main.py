from .normalizer import DataNormalizer
import os

def main():
    db_path = "code_python/data-normalization/normalized.db"
    db_url = f"sqlite:///{db_path}"

    csv_path = "code_python/data-normalization/data/raw_data.csv"

    # Clean up old db if exists for clean run
    if os.path.exists(db_path):
        os.remove(db_path)

    normalizer = DataNormalizer(db_url)
    normalizer.init_db()
    normalizer.normalize_csv(csv_path)

    # Validation Query
    from sqlalchemy import text
    with normalizer.engine.connect() as conn:
        print("\n--- Normalization Report ---")
        customers = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        products = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        orders = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
        items = conn.execute(text("SELECT COUNT(*) FROM order_items")).scalar()

        print(f"Customers: {customers}")
        print(f"Products:  {products}")
        print(f"Orders:    {orders}")
        print(f"Items:     {items}")
        print("----------------------------")

if __name__ == "__main__":
    main()
