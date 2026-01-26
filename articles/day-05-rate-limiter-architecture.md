# Day 05: Scalable Rate Limiter Architecture

In distributed systems, controlling the flow of traffic is crucial to prevent resource exhaustion and ensure fair usage. A naive implementation of a rate limiter often falls prey to race conditions, where concurrent requests slip through due to the "Check-Then-Act" gap. Today, we built a robust, thread-safe rate limiter implementing the Token Bucket algorithm.

## The Problem: Race Conditions in Rate Limiting

A common mistake in rate limiting logic looks like this:

```python
# BAD: Race condition vulnerability
current_tokens = redis.get(key)
if current_tokens >= cost:
    redis.decr(key, cost)
    return True
else:
    return False
```

Between the `get` (Check) and `decr` (Act), another process might have consumed the tokens. In high-concurrency environments, this leads to allowing significantly more requests than the limit permits.

## The Solution: Atomic Token Buckets

To solve this, state modification must be atomic.
1. **Token Bucket Algorithm**: We model the limit as a bucket of tokens. Tokens are added at a constant rate (refill rate) up to a maximum capacity (burst size). Each request consumes a token.
2. **Atomicity**: We must lock the bucket or use atomic operations (like Lua scripts in Redis) to ensure that the calculation of available tokens and the decrement happen in a single, indivisible step.

## Implementation

Our implementation separates the core logic from the storage backend, allowing for pluggable architectures (In-Memory, Redis, Memcached).

### The Storage Interface

We defined an abstract base class `RateLimitStorage` enforcing an atomic `take_token` method.

```python
class RateLimitStorage(abc.ABC):
    @abc.abstractmethod
    def take_token(self, key: str, capacity: int, refill_rate: float, cost: int = 1) -> bool:
        pass
```

### In-Memory Thread Safety

For the in-memory implementation, we utilized `threading.Lock` to protect the critical section. We also used `time.monotonic()` instead of `time.time()` to prevent issues if the system clock changes (e.g., NTP updates).

```python
with self._lock:
    current_time = time.monotonic()
    # ... calculate refill ...
    if tokens >= cost:
        tokens -= cost
        self._buckets[key] = (tokens, last_refill)
        return True
```

## Use Cases

1. **API Throttling**: Protect backend services from spikes in traffic.
2. **Brute Force Protection**: Limit login attempts per IP.
3. **Feature Access Control**: Metered usage for SaaS tiers.

This architecture serves as a foundation. In a production distributed environment, we would swap the `InMemoryStorage` for a `RedisStorage` using Lua scripts to maintain the same atomicity guarantees across multiple server instances.
