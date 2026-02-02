import pytest
from pydantic import ValidationError
from src.validators import validate_sku, validate_phone_number
from src.models import Order, Customer, Product, Address
from src.processor import validate_batch

# --- Validators Tests ---
def test_validate_sku():
    assert validate_sku("ABC-123") is True
    assert validate_sku("A-1") is False # Too short
    assert validate_sku("abc-123") is False # Lowercase

def test_validate_phone():
    assert validate_phone_number("+15551234567") is True
    assert validate_phone_number("15551234567") is False # Missing +
    assert validate_phone_number("+1") is False # Too short

# --- Models Tests ---
def test_product_sku_validation():
    with pytest.raises(ValidationError) as excinfo:
        Product(
            sku="bad",
            name="Test Product",
            price=10.0,
            currency="USD",
            stock_quantity=5
        )
    assert "Invalid SKU format" in str(excinfo.value)

def test_order_math_validation():
    # Valid order
    order_data = {
        "order_id": "ORD-001",
        "customer_id": 1,
        "items": [{"product_sku": "SKU-001", "quantity": 2, "unit_price": 10.0}],
        "total_amount": 20.0,
        "discount_amount": 0.0
    }
    order = Order(**order_data)
    assert order.total_amount == 20.0

    # Invalid math
    order_data["total_amount"] = 50.0
    with pytest.raises(ValidationError) as excinfo:
        Order(**order_data)
    assert "Total amount 50.0 does not match" in str(excinfo.value)

def test_order_discount_too_high():
    order_data = {
        "order_id": "ORD-002",
        "customer_id": 1,
        "items": [{"product_sku": "SKU-001", "quantity": 1, "unit_price": 10.0}],
        "total_amount": 0.0,
        "discount_amount": 20.0 # > 10.0
    }
    with pytest.raises(ValidationError) as excinfo:
        Order(**order_data)
    assert "Discount amount cannot exceed the subtotal" in str(excinfo.value)

# --- Processor Tests ---
def test_validate_batch():
    data = [
        # Valid
        {
            "order_id": "ORD-100",
            "customer_id": 1,
            "items": [{"product_sku": "SKU-100", "quantity": 1, "unit_price": 100.0}],
            "total_amount": 100.0,
            "discount_amount": 0.0
        },
        # Invalid
        {
            "order_id": "ORD-101",
            "customer_id": 1,
            "items": [{"product_sku": "bad", "quantity": 1, "unit_price": 100.0}],
            "total_amount": 100.0,
            "discount_amount": 0.0
        }
    ]

    report = validate_batch(data, Order)
    assert report.valid_count == 1
    assert report.error_count == 1
    assert report.valid_records[0].order_id == "ORD-100"
    assert "Invalid SKU format" in report.errors[0]['error_messages'][0]
