# Async Producer-Consumer Simulation

A high-performance simulation of a Queue-based Producer-Consumer architecture using Python's `asyncio`.

## Features

*   **Priority Queueing**: Events are processed based on priority (lower value = higher urgency), not just FIFO.
*   **Backpressure Handling**: The broker enforces a maximum queue size, causing producers to drop messages if the consumers cannot keep up.
*   **Graceful Shutdown**: Implements a robust shutdown sequence that cancels producers, drains the queue, and then stops consumers.
*   **Immutable Data Models**: Uses Pydantic V2 for frozen, type-safe event payloads.

## Usage

Run the simulation:

```bash
# From code_python/streaming-sim directory
python3 -m src.main
```

Run tests:

```bash
pytest tests/
```
