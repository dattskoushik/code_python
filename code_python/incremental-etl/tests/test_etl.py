import pytest
import sys
import os
from sqlalchemy.pool import StaticPool

# Ensure src is in path
sys.path.append(os.getcwd())

from src.etl import IncrementalLoader
from src.storage import Storage

@pytest.fixture
def storage():
    # Use in-memory SQLite with StaticPool for persistence across session usage in test
    s = Storage(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={'check_same_thread': False}
    )
    s.init_db()
    yield s
    s.close()

def test_hash_computation(storage):
    loader = IncrementalLoader(storage)
    data = {"id": 1, "name": "Test", "email": "test@example.com", "status": "active"}

    # Hash should be consistent
    h1 = loader._compute_hash(data)
    h2 = loader._compute_hash(data)
    assert h1 == h2

    # ID should be ignored in hash
    data2 = {"id": 999, "name": "Test", "email": "test@example.com", "status": "active"}
    h3 = loader._compute_hash(data2)
    assert h1 == h3

    # Content change should change hash
    data3 = {"id": 1, "name": "Test Changed", "email": "test@example.com", "status": "active"}
    h4 = loader._compute_hash(data3)
    assert h1 != h4

def test_process_lifecycle(storage):
    loader = IncrementalLoader(storage)

    # 1. Insert
    data = [{"id": 1, "name": "Alice", "email": "alice@example.com", "status": "active"}]
    stats = loader.process(data)
    assert stats["inserted"] == 1
    assert stats["updated"] == 0
    assert stats["unchanged"] == 0
    assert stats["errors"] == 0

    # Verify DB
    state = storage.get_current_state()
    assert 1 in state

    # 2. Unchanged
    stats = loader.process(data)
    assert stats["inserted"] == 0
    assert stats["updated"] == 0
    assert stats["unchanged"] == 1

    # 3. Update
    data_mod = [{"id": 1, "name": "Alice Modified", "email": "alice@example.com", "status": "active"}]
    stats = loader.process(data_mod)
    assert stats["inserted"] == 0
    assert stats["updated"] == 1
    assert stats["unchanged"] == 0

    # Verify DB hash changed
    new_state = storage.get_current_state()
    assert new_state[1] != state[1]

def test_validation_error(storage):
    loader = IncrementalLoader(storage)
    data = [{"id": 1, "name": "Bad", "email": "not-an-email", "status": "active"}]
    stats = loader.process(data)
    assert stats["errors"] == 1
    assert len(stats["error_list"]) == 1
    assert stats["inserted"] == 0
