"""
models.py

Pydantic V2 models for the Validation Layer.
"""
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict
from .validators import validate_sku, validate_phone_number, validate_currency_code

class Address(BaseModel):
    street: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2)
    zip_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")
    country: str = Field("USA", min_length=2)

    model_config = ConfigDict(frozen=True)

class Customer(BaseModel):
    id: int = Field(..., gt=0)
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    address: Address
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v: str) -> str:
        if v and not validate_phone_number(v):
            raise ValueError("Invalid phone number format. Must be E.164 (e.g., +15555555555).")
        return v

class Product(BaseModel):
    sku: str
    name: str = Field(..., min_length=3)
    price: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    stock_quantity: int = Field(..., ge=0)

    @field_validator("sku")
    @classmethod
    def check_sku(cls, v: str) -> str:
        if not validate_sku(v):
            raise ValueError("Invalid SKU format. Expected pattern XXX-XXX.")
        return v

    @field_validator("currency")
    @classmethod
    def check_currency(cls, v: str) -> str:
        if not validate_currency_code(v):
            raise ValueError(f"Unsupported currency code: {v}")
        return v

class LineItem(BaseModel):
    product_sku: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)

    @field_validator("product_sku")
    @classmethod
    def check_sku(cls, v: str) -> str:
        if not validate_sku(v):
            raise ValueError("Invalid SKU format.")
        return v

class Order(BaseModel):
    order_id: str = Field(..., min_length=5)
    customer_id: int = Field(..., gt=0)
    items: List[LineItem] = Field(..., min_length=1)
    total_amount: float = Field(..., ge=0)
    discount_amount: float = Field(0.0, ge=0)
    placed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode='after')
    def check_totals(self) -> 'Order':
        # 1. Verify calculated total matches sum of items (approximate)
        calculated_subtotal = sum(item.quantity * item.unit_price for item in self.items)

        # 2. Verify discount is not greater than subtotal
        if self.discount_amount > calculated_subtotal:
            raise ValueError("Discount amount cannot exceed the subtotal.")

        # 3. Verify final total matches (subtotal - discount)
        expected_total = calculated_subtotal - self.discount_amount

        # Allow small float error
        if abs(self.total_amount - expected_total) > 0.01:
            raise ValueError(f"Total amount {self.total_amount} does not match sum of items minus discount ({expected_total}).")

        return self
