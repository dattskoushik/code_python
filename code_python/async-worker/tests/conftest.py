import pytest
import pytest_asyncio
import asyncio
import os
from pathlib import Path
from src.database import init_db
import src.main

TEST_DB = Path("test_jobs.db")

@pytest_asyncio.fixture(loop_scope="function")
async def test_db():
    if TEST_DB.exists():
        os.remove(TEST_DB)

    await init_db(TEST_DB)

    # Patch the global job_manager in main
    original_path = src.main.job_manager.db_path
    src.main.job_manager.db_path = TEST_DB

    yield TEST_DB

    # Cleanup
    src.main.job_manager.db_path = original_path
    if TEST_DB.exists():
        os.remove(TEST_DB)

@pytest.fixture
def override_get_db(test_db):
    from src.database import get_db
    async def _get_db_override():
        async for db in get_db(test_db):
            yield db
    return _get_db_override
