import json
import uuid
from .models import CustomerProfile, OrderRequest
from .engine import validate_dataset

def main():
    print("--- 1. Validating Customer Profiles ---")

    customers_data = [
        # Valid
        {
            "id": str(uuid.uuid4()),
            "email": "alice@example.com",
            "phone": "+14155550100",
            "password": "Password1!",
            "age": 30
        },
        # Invalid email
        {
            "id": str(uuid.uuid4()),
            "email": "bob_at_example.com",
            "phone": "+14155550101",
            "password": "Password1!",
            "age": 25
        },
        # Weak password
        {
            "id": str(uuid.uuid4()),
            "email": "charlie@example.com",
            "phone": "+14155550102",
            "password": "123",
            "age": 20
        },
        # Invalid Phone
         {
            "id": str(uuid.uuid4()),
            "email": "dave@example.com",
            "phone": "555-0103",
            "password": "Password1!",
            "age": 40
        }
    ]

    result = validate_dataset(customers_data, CustomerProfile)
    # default=str handles UUID serialization
    print(json.dumps(result, indent=2, default=str))

    print("\n--- 2. Validating Orders (Cross-field checks) ---")

    orders_data = [
        # Valid
        {
            "order_id": "ORD-001",
            "customer_id": str(uuid.uuid4()),
            "items": [
                {"product_id": "P1", "quantity": 2, "unit_price": 10.0},
                {"product_id": "P2", "quantity": 1, "unit_price": 5.50}
            ],
            "total_amount": 25.50
        },
        # Invalid Total (Business Logic Error)
        {
            "order_id": "ORD-002",
            "customer_id": str(uuid.uuid4()),
            "items": [
                {"product_id": "P1", "quantity": 2, "unit_price": 10.0}
            ],
            "total_amount": 100.00 # Should be 20.0
        }
    ]

    result_orders = validate_dataset(orders_data, OrderRequest)
    print(json.dumps(result_orders, indent=2, default=str))

if __name__ == "__main__":
    main()
