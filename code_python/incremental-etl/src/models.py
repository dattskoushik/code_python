from pydantic import BaseModel, ConfigDict

class ProductSource(BaseModel):
    """
    Represents a raw record from the source system.
    Using frozen=True for immutability as per memory guidelines.
    """
    id: int
    name: str
    category: str
    price: float
    stock: int

    model_config = ConfigDict(frozen=True)
