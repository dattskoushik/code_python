from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict
from .validators import is_valid_phone, is_strong_password

class CustomerProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    email: EmailStr
    phone: str
    password: str = Field(exclude=True) # exclude from serialization
    age: int = Field(ge=18, le=120)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not is_valid_phone(v):
            raise ValueError('Invalid phone number format. Must be E.164')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not is_strong_password(v):
            raise ValueError('Password must be at least 8 chars, contain upper, lower, digit, and special char')
        return v

class OrderItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_id: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)

class OrderRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    order_id: str
    customer_id: UUID
    items: List[OrderItem]
    total_amount: float = Field(gt=0)
    discount_code: Optional[str] = None

    @model_validator(mode='after')
    def verify_total(self) -> 'OrderRequest':
        calculated_total = sum(item.quantity * item.unit_price for item in self.items)
        # Float comparison with tolerance
        if abs(calculated_total - self.total_amount) > 0.01:
            raise ValueError(f'Total amount {self.total_amount} does not match sum of items {calculated_total}')
        return self
