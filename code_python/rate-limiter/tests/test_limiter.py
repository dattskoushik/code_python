import threading
import time
import pytest
from src.limiter import RateLimiter
from src.storage import InMemoryStorage

def test_basic_allow():
    storage = InMemoryStorage()
    limiter = RateLimiter(storage)
    key = "user_basic"
    # Capacity 10, refill 1/s.
    assert limiter.allow_request(key, 10, 1) is True

def test_exhaust_capacity():
    storage = InMemoryStorage()
    limiter = RateLimiter(storage)
    key = "user_exhaust"
    capacity = 2
    refill_rate = 1

    # Consuming 1 token each time
    assert limiter.allow_request(key, capacity, refill_rate) is True # 1/2 used
    assert limiter.allow_request(key, capacity, refill_rate) is True # 2/2 used
    assert limiter.allow_request(key, capacity, refill_rate) is False # Empty

def test_refill_logic():
    storage = InMemoryStorage()
    limiter = RateLimiter(storage)
    key = "user_refill"
    capacity = 1
    refill_rate = 10.0 # 10 tokens per second

    # Consume 1 (empty)
    assert limiter.allow_request(key, capacity, refill_rate) is True
    assert limiter.allow_request(key, capacity, refill_rate) is False

    # Wait 0.15s -> should get 1.5 tokens -> capped at 1.
    time.sleep(0.15)
    assert limiter.allow_request(key, capacity, refill_rate) is True

def test_concurrency():
    """
    Test that concurrent requests are handled correctly and exactly 'capacity' requests succeed.
    """
    storage = InMemoryStorage()
    limiter = RateLimiter(storage)
    key = "concurrent_user"
    capacity = 100
    refill_rate = 0.0 # No refill to simplify counting

    results = []
    # We need a thread-safe list append or just rely on GIL for list append (which is atomic-ish but let's be safe)
    # Actually list append is thread safe in CPython, but let's not rely on it.
    results_lock = threading.Lock()

    def worker():
        res = limiter.allow_request(key, capacity, refill_rate)
        with results_lock:
            results.append(res)

    threads = []
    # Launch 150 threads, only 100 should succeed
    for _ in range(150):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    success = results.count(True)
    fail = results.count(False)

    assert success == 100
    assert fail == 50
