import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Adjust path to find src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import ProductSource
from src.db import Base, ProductModel
from src.etl import detect_changes, load_changes, get_target_state, compute_row_hash

@pytest.fixture
def session():
    # In-memory SQLite with StaticPool for test isolation
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_initial_load(session):
    source_data = [
        ProductSource(id=1, name="A", category="C", price=10.0, stock=10),
        ProductSource(id=2, name="B", category="C", price=20.0, stock=20),
    ]

    target_map = get_target_state(session) # Empty
    to_insert, to_update, unchanged = detect_changes(source_data, target_map)

    assert len(to_insert) == 2
    assert len(to_update) == 0
    assert len(unchanged) == 0

    load_changes(session, to_insert, to_update)

    # Verify DB
    rows = session.query(ProductModel).order_by(ProductModel.id).all()
    assert len(rows) == 2
    assert rows[0].name == "A"
    assert rows[0].row_hash == compute_row_hash(source_data[0])

def test_update_load(session):
    # Setup initial state
    initial_source = ProductSource(id=1, name="A", category="C", price=10.0, stock=10)
    h1 = compute_row_hash(initial_source)

    p1 = ProductModel(id=1, name="A", category="C", price=10.0, stock=10, row_hash=h1)
    session.add(p1)
    session.commit()

    # Now simulate update
    updated_source = ProductSource(id=1, name="A", category="C", price=15.0, stock=10) # Price changed
    target_map = get_target_state(session)

    to_insert, to_update, unchanged = detect_changes([updated_source], target_map)

    assert len(to_insert) == 0
    assert len(to_update) == 1
    assert len(unchanged) == 0

    load_changes(session, to_insert, to_update)

    row = session.query(ProductModel).filter_by(id=1).first()
    assert row.price == 15.0
    assert row.row_hash != h1
    assert row.row_hash == compute_row_hash(updated_source)

def test_no_change(session):
    src = ProductSource(id=1, name="A", category="C", price=10.0, stock=10)
    h = compute_row_hash(src)

    p = ProductModel(id=1, name="A", category="C", price=10.0, stock=10, row_hash=h)
    session.add(p)
    session.commit()

    target_map = get_target_state(session)
    to_insert, to_update, unchanged = detect_changes([src], target_map)

    assert len(to_insert) == 0
    assert len(to_update) == 0
    assert len(unchanged) == 1
