import time
import threading
import random
from src.limiter import RateLimiter
from src.storage import InMemoryStorage

def simulate_user(user_id: str, limiter: RateLimiter):
    """
    Simulates a user making requests at random intervals.
    """
    # Rate limit: 5 requests burst, refill 1 request per second.
    capacity = 5
    refill_rate = 1.0

    for i in range(10):
        allowed = limiter.allow_request(user_id, capacity, refill_rate)
        status = "ALLOWED" if allowed else "DENIED"
        print(f"[{time.strftime('%H:%M:%S')}] User {user_id}: Request {i+1} -> {status}")
        # Sleep for a bit to simulate real world usage
        time.sleep(random.uniform(0.1, 1.5))

def main():
    print("Initializing Rate Limiter Demo...")
    storage = InMemoryStorage()
    limiter = RateLimiter(storage)

    threads = []
    # Simulate 3 users running concurrently
    for i in range(1, 4):
        user_id = f"user_{i}"
        t = threading.Thread(target=simulate_user, args=(user_id, limiter))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Simulation complete.")

if __name__ == "__main__":
    main()
