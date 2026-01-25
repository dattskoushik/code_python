# Day 05: Designing High-Throughput Rate Limiters

**Author:** dattskoushik
**Date:** Current
**Focus:** Rate Limiting, Token Bucket, Distributed Systems

---

## The Problem: The Thundering Herd

In the lifecycle of any public-facing API, there comes a moment when traffic spikes from "healthy growth" to "system-threatening." Without traffic control, a single misconfigured script or a malicious actor can exhaust database connections, CPU cycles, and memory, causing a cascading failure that takes down the entire platform for all users.

Naive solutions often involve "Fixed Window" counters (e.g., "100 requests per minute"). However, these suffer from the "boundary burst" issue: a user can send 100 requests at 11:59:59 and another 100 at 12:00:01, effectively doubling the allowed rate in a two-second window.

We need a solution that is smooth, predictable, and capable of handling legitimate burstiness (like a dashboard loading) while capping sustained throughput.

## The Solution: Token Bucket Algorithm

For this project, I implemented a robust **Token Bucket** rate limiter. Unlike fixed windows, the Token Bucket analogy is intuitive:
1.  A bucket holds a maximum number of tokens (Capacity).
2.  Tokens are added to the bucket at a fixed rate (Refill Rate).
3.  Each request consumes one token.
4.  If the bucket is empty, the request is rejected.

This allows for *bursts* (consuming accumulated tokens) but enforces a long-term average rate.

### Architecture

I designed the system with modularity and concurrency in mind. The core `RateLimiter` delegates the atomic "check-and-consume" operation to the `StorageBackend`.

-   **`RateLimiter`**: A facade that provides the user-friendly API.
-   **`StorageBackend`**: Handles the state and ensures atomicity. I implemented a `take_token` method in `InMemoryStorage` that locks, calculates, and updates in a single critical section.

This mirrors how production systems work: the "logic" is often pushed to the data store (e.g., using Redis Lua scripts) to avoid race conditions between reading and writing.

```python
# Atomic consumption inside StorageBackend
with self._lock:
    # ... calculate refill ...
    if tokens >= 1:
        tokens -= 1
        self._storage[key] = ...
        return True
    return False
```

## Use Cases

1.  **SaaS API Tiering**: Enforcing limits based on subscription levels (e.g., Free Tier: 5 req/s, Enterprise: 100 req/s).
2.  **Login Protection**: Limiting attempts on `/login` endpoints to prevent brute-force attacks on user accounts.
3.  **Background Job Throttling**: Preventing internal workers from overwhelming a third-party API or a fragile legacy database.

## Moving Forward

While the in-memory solution is perfect for single-instance microservices, a distributed setup would require a transition to Redis with Lua scripts to ensure atomicity across nodes. That is the natural next step for scaling this architecture.
