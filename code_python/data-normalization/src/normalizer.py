import csv
import logging
from typing import Dict, Any
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from datetime import datetime

from .models import Base, Customer, Product, Order, OrderItem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataNormalizer:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.session = Session(self.engine)

    def init_db(self):
        """Creates the database tables."""
        logger.info("Initializing database schema...")
        Base.metadata.create_all(self.engine)

    def normalize_csv(self, csv_path: str):
        """
        Reads a raw CSV and normalizes it into relational tables.
        """
        logger.info(f"Starting normalization for {csv_path}...")

        # In-memory caches to minimize DB lookups for repeated entities in the same batch
        # We also need to preload existing entities if we were doing incremental updates,
        # but for this specific 'job', we assume we can just check DB on miss.
        customer_cache: Dict[str, Customer] = {}
        product_cache: Dict[str, Product] = {}
        order_cache: Dict[str, Order] = {}

        try:
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                rows_processed = 0
                for row in reader:
                    self._process_row(row, customer_cache, product_cache, order_cache)
                    rows_processed += 1

                self.session.commit()
                logger.info(f"Successfully processed {rows_processed} rows.")

        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def _process_row(
        self,
        row: Dict[str, Any],
        customer_cache: Dict[str, Customer],
        product_cache: Dict[str, Product],
        order_cache: Dict[str, Order]
    ):
        # 1. Handle Customer
        email = row['customer_email']
        if email not in customer_cache:
            # Check DB
            stmt = select(Customer).where(Customer.email == email)
            customer = self.session.execute(stmt).scalar_one_or_none()

            if not customer:
                customer = Customer(name=row['customer_name'], email=email)
                self.session.add(customer)
                # Flush to assign ID if needed by other logic, though ORM handles relationship obj links fine
                self.session.flush()

            customer_cache[email] = customer

        customer = customer_cache[email]

        # 2. Handle Product
        product_name = row['product_name']
        if product_name not in product_cache:
            stmt = select(Product).where(Product.name == product_name)
            product = self.session.execute(stmt).scalar_one_or_none()

            if not product:
                product = Product(
                    name=product_name,
                    category=row['category'],
                    current_price=float(row['unit_price'])
                )
                self.session.add(product)
                self.session.flush()

            product_cache[product_name] = product

        product = product_cache[product_name]

        # 3. Handle Order
        # Assumption: transaction_id is unique per order. Multiple rows with same transaction_id
        # constitute a single order with multiple items.
        transaction_id = row['transaction_id']

        if transaction_id not in order_cache:
            stmt = select(Order).where(Order.id == transaction_id)
            order = self.session.execute(stmt).scalar_one_or_none()

            if not order:
                order = Order(
                    id=transaction_id,
                    customer=customer,
                    date=datetime.fromisoformat(row['timestamp'])
                )
                self.session.add(order)
                # No need to flush immediately unless we need order.id, which we already have

            order_cache[transaction_id] = order

        order = order_cache[transaction_id]

        # 4. Create Order Item
        # We always create a new item for the row.
        # (Assuming rows don't repeat the exact same product for the same order, or if they do, it's separate line items)

        order_item = OrderItem(
            order=order,
            product=product,
            quantity=int(row['quantity']),
            unit_price_at_purchase=float(row['unit_price'])
        )
        self.session.add(order_item)
