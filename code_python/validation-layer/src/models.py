from decimal import Decimal
from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator, model_validator

from .validators import SKU_PATTERN, PHONE_PATTERN, validate_not_future

class Customer(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: EmailStr
    phone: str = Field(pattern=PHONE_PATTERN)
    age: int = Field(ge=18, le=120)

class OrderItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    sku: str = Field(pattern=SKU_PATTERN, description="SKU format: ABC-12345")
    quantity: int = Field(gt=0)
    price: Decimal = Field(gt=0, decimal_places=2)

class Order(BaseModel):
    model_config = ConfigDict(frozen=True)

    order_id: UUID = Field(default_factory=uuid4)
    customer: Customer
    items: List[OrderItem] = Field(min_length=1)
    total_amount: Decimal = Field(gt=0, decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator('created_at')
    @classmethod
    def check_future_date(cls, v: datetime) -> datetime:
        return validate_not_future(v)

    @model_validator(mode='after')
    def check_total_amount(self) -> 'Order':
        calculated_total = sum(item.price * item.quantity for item in self.items)
        if self.total_amount != calculated_total:
            raise ValueError(f"Total amount {self.total_amount} does not match sum of items {calculated_total}")
        return self
