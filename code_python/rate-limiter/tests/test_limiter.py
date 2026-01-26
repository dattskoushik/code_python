import time
import pytest
import threading
import sys
import os

# Ensure src is in path if running from repo root
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from src.limiter import RateLimiter, limit_requests, RateLimitExceeded
from src.storage import InMemoryStorage

def test_allow_request_basic():
    storage = InMemoryStorage()
    limiter = RateLimiter(storage)
    # Capacity 5, rate 1/s
    assert limiter.allow_request("user1", 5, 1.0) is True

def test_block_request_exceeded():
    storage = InMemoryStorage()
    limiter = RateLimiter(storage)
    # Capacity 1, rate 0.1/s (slow refill)
    assert limiter.allow_request("user2", 1, 0.1) is True
    assert limiter.allow_request("user2", 1, 0.1) is False

def test_refill_mechanism():
    storage = InMemoryStorage()
    limiter = RateLimiter(storage)
    # Capacity 1, rate 10/s (fast refill)
    assert limiter.allow_request("user3", 1, 10.0) is True
    assert limiter.allow_request("user3", 1, 10.0) is False

    # Wait for refill (0.11s should give 1.1 tokens)
    time.sleep(0.11)
    assert limiter.allow_request("user3", 1, 10.0) is True

def test_decorator():
    storage = InMemoryStorage()

    # Updated lambda to accept args, making it safe for wrapper
    @limit_requests(lambda *args, **kwargs: "static_key", capacity=2, refill_rate=1, storage=storage)
    def my_func():
        return "success"

    assert my_func() == "success"
    assert my_func() == "success"

    with pytest.raises(RateLimitExceeded):
        my_func()

def test_thread_safety():
    storage = InMemoryStorage()
    limiter = RateLimiter(storage)
    # Capacity 100

    success_count = 0
    lock = threading.Lock()

    def task():
        nonlocal success_count
        # High capacity to ensure no false negatives due to time,
        # but we want to test race conditions on the "get, check, set" logic.
        # If we slam it with 150 requests for capacity 100, exactly 100 should pass.
        if limiter.allow_request("concurrent_key", 100, 1):
            with lock:
                success_count += 1

    threads = [threading.Thread(target=task) for _ in range(150)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Should have exactly 100 successes
    assert success_count == 100
