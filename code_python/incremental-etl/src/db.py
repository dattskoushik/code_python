from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class ProductModel(Base):
    """
    SQLAlchemy model for the target data warehouse table.
    Includes `row_hash` to facilitate incremental ETL.
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    row_hash = Column(String, nullable=False, index=True)

def get_engine(db_url="sqlite:///etl.db"):
    return create_engine(db_url)

def get_session_factory(engine):
    return sessionmaker(bind=engine)

def init_db(engine):
    Base.metadata.create_all(engine)
