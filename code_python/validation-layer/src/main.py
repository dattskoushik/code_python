"""
main.py

Demonstration script for the Validation Layer.
"""
import json
from .models import Order
from .processor import validate_batch

def main():
    print("=== Validation Layer Demo ===\n")

    # Sample data: Mix of valid and invalid orders
    raw_orders = [
        # 1. Valid Order
        {
            "order_id": "ORD-12345",
            "customer_id": 101,
            "items": [
                {"product_sku": "SKU-001", "quantity": 2, "unit_price": 50.0},
                {"product_sku": "SKU-002", "quantity": 1, "unit_price": 100.0}
            ],
            "total_amount": 200.0,
            "discount_amount": 0.0
        },
        # 2. Invalid: Bad SKU format
        {
            "order_id": "ORD-67890",
            "customer_id": 102,
            "items": [
                {"product_sku": "bad_sku", "quantity": 1, "unit_price": 50.0}
            ],
            "total_amount": 50.0,
            "discount_amount": 0.0
        },
        # 3. Invalid: Total amount mismatch (Math error)
        {
            "order_id": "ORD-11121",
            "customer_id": 103,
            "items": [
                {"product_sku": "SKU-001", "quantity": 2, "unit_price": 10.0} # Sum = 20
            ],
            "total_amount": 100.0, # Expected 20
            "discount_amount": 0.0
        },
        # 4. Invalid: Discount > Subtotal
        {
            "order_id": "ORD-33333",
            "customer_id": 104,
            "items": [
                {"product_sku": "SKU-001", "quantity": 1, "unit_price": 100.0}
            ],
            "total_amount": 0.0,
            "discount_amount": 150.0
        }
    ]

    print(f"Processing {len(raw_orders)} records...\n")
    report = validate_batch(raw_orders, Order)

    print(f"✅ Valid Records: {report.valid_count}")
    for valid in report.valid_records:
        print(f"   - Order {valid.order_id} verified.")

    print(f"\n❌ Invalid Records: {report.error_count}")
    for error in report.errors:
        print(f"   [Record Index {error['index']}]")
        for msg in error['error_messages']:
            print(f"     -> {msg}")
        print("-" * 40)

if __name__ == "__main__":
    main()
