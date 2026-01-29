from typing import List
from datetime import datetime
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    orders: Mapped[List["Order"]] = relationship(back_populates="customer")

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, email='{self.email}')>"

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    category: Mapped[str] = mapped_column(String(50))
    current_price: Mapped[float] = mapped_column(Float)

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}')>"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(50), primary_key=True) # Using string ID from CSV if unique, or we can auto-increment.
    # Actually, CSV usually has a Transaction ID. Let's use that as PK or store it.
    # Let's assume the CSV Transaction ID is the Order ID.

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    date: Mapped[datetime] = mapped_column(DateTime)

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order")

    def __repr__(self) -> str:
        return f"<Order(id='{self.id}', date='{self.date}')>"

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_at_purchase: Mapped[float] = mapped_column(Float)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()

    def __repr__(self) -> str:
        return f"<OrderItem(order='{self.order_id}', product='{self.product_id}', qty={self.quantity})>"
