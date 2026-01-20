from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL
# Using a file-based SQLite database.
SQLALCHEMY_DATABASE_URL = "sqlite:///./ingestion.db"

# Create engine
# connect_args={"check_same_thread": False} is needed for SQLite to allow multiple threads
# to interact with the database, which is common in FastAPI (though SQLite handles it safely with WAL)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency helper to yield a database session.
    Ensures the session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
