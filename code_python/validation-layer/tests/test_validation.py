import pytest
from uuid import uuid4
from src.validators import is_valid_phone, luhn_check, is_strong_password
from src.models import CustomerProfile, OrderRequest
from src.engine import validate_dataset
from pydantic import ValidationError

def test_validators():
    assert is_valid_phone("+14155552671")
    assert not is_valid_phone("4155552671")

    # Example valid Luhn number
    assert luhn_check("79927398713")
    assert not luhn_check("79927398710")

    assert is_strong_password("Password1!")
    assert not is_strong_password("weak")
    assert not is_strong_password("NoSpecialChar1")

def test_customer_model():
    # Valid
    CustomerProfile(
        id=uuid4(),
        email="test@example.com",
        phone="+1234567890",
        password="Password1!",
        age=25
    )

    # Invalid Phone
    with pytest.raises(ValidationError):
        CustomerProfile(
            id=uuid4(),
            email="test@example.com",
            phone="bad-phone",
            password="Password1!",
            age=25
        )

def test_order_model_logic():
    # Valid
    OrderRequest(
        order_id="1",
        customer_id=uuid4(),
        items=[{"product_id": "p1", "quantity": 1, "unit_price": 10.0}],
        total_amount=10.0
    )

    # Invalid Total
    with pytest.raises(ValidationError) as excinfo:
        OrderRequest(
            order_id="1",
            customer_id=uuid4(),
            items=[{"product_id": "p1", "quantity": 1, "unit_price": 10.0}],
            total_amount=50.0
        )
    assert "match sum of items" in str(excinfo.value)

def test_engine():
    data = [
        {"id": str(uuid4()), "email": "a@b.com", "phone": "+1234567890", "password": "Password1!", "age": 20},
        {"id": str(uuid4()), "email": "invalid", "phone": "+1234567890", "password": "Password1!", "age": 20}
    ]
    result = validate_dataset(data, CustomerProfile)
    assert result["valid_count"] == 1
    assert result["invalid_count"] == 1
    # Check that the error message mentions the invalid field
    assert "email" in result["errors"][0]["errors"][0].lower()
