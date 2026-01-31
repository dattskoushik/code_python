import sys
import os
from pathlib import Path
from decimal import Decimal
import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta

# Add project root to sys.path
# We are in code_python/validation-layer/tests
# Root is code_python/validation-layer
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.models import Order, Customer, OrderItem
from src.processor import process_batch

def test_customer_validation():
    # Valid
    c = Customer(email="test@example.com", phone="+1234567890", age=25)
    assert c.age == 25

    # Invalid email
    with pytest.raises(ValidationError):
        Customer(email="bad-email", phone="+1234567890", age=25)

    # Invalid age
    with pytest.raises(ValidationError):
        Customer(email="test@example.com", phone="+1234567890", age=17)

def test_order_item_validation():
    # Valid
    item = OrderItem(sku="ABC-12345", quantity=1, price=Decimal("10.00"))
    assert item.sku == "ABC-12345"

    # Invalid SKU
    with pytest.raises(ValidationError):
        OrderItem(sku="abc-12345", quantity=1, price=Decimal("10.00"))

    # Invalid Price
    with pytest.raises(ValidationError):
        OrderItem(sku="ABC-12345", quantity=1, price=Decimal("-10.00"))

def test_order_total_validation():
    customer = Customer(email="t@e.com", phone="+123", age=20)
    item = OrderItem(sku="ABC-12345", quantity=2, price=Decimal("10.00"))

    # Valid total (2 * 10 = 20)
    order = Order(customer=customer, items=[item], total_amount=Decimal("20.00"))
    assert order.total_amount == 20.00

    # Invalid total
    with pytest.raises(ValidationError) as exc:
        Order(customer=customer, items=[item], total_amount=Decimal("19.00"))
    assert "match sum of items" in str(exc.value)

def test_future_date_validation():
    customer = Customer(email="t@e.com", phone="+123", age=20)
    item = OrderItem(sku="ABC-12345", quantity=1, price=Decimal("10.00"))

    future_date = datetime.now() + timedelta(days=1)

    with pytest.raises(ValidationError) as exc:
        Order(
            customer=customer,
            items=[item],
            total_amount=Decimal("10.00"),
            created_at=future_date
        )
    assert "Date cannot be in the future" in str(exc.value)

def test_processor_batch():
    data = [
        {
            "customer": {"email": "a@b.com", "phone": "+15555555", "age": 20},
            "items": [{"sku": "ABC-12345", "quantity": 1, "price": 10.0}],
            "total_amount": 10.0
        },
        {
            "customer": {"email": "bad", "phone": "+15555555", "age": 20},
            "items": [{"sku": "ABC-12345", "quantity": 1, "price": 10.0}],
            "total_amount": 10.0
        }
    ]

    result = process_batch(data)
    assert len(result.valid_orders) == 1
    assert len(result.errors) == 1
    assert result.errors[0]["index"] == 1
    # Check if we can find the email error in the string representation or structure
    errors_found = False
    for err in result.errors[0]["validation_errors"]:
        if "email" in str(err):
            errors_found = True
            break
        # Or check location
        if "email" in err['loc']:
             errors_found = True
             break

    assert errors_found
