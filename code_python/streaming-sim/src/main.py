import asyncio
import logging
import sys
from .broker import MessageBroker
from .worker import Producer, Consumer

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

async def main():
    broker = MessageBroker(maxsize=10) # Small queue to force backpressure/priority logic

    # Create Workers
    producers = [
        Producer(broker, "P1", interval=0.2),
        Producer(broker, "P2", interval=0.3)
    ]

    consumers = [
        Consumer(broker, "C1", processing_time=0.5),
        Consumer(broker, "C2", processing_time=0.4)
    ]

    # Start Tasks
    producer_tasks = [asyncio.create_task(p.run()) for p in producers]
    consumer_tasks = [asyncio.create_task(c.run()) for c in consumers]

    logging.info("Simulation started. Running for 5 seconds...")
    await asyncio.sleep(5)

    # Graceful Shutdown Sequence
    logging.info("Stopping producers...")
    for task in producer_tasks:
        task.cancel()
    # Wait for producers to cleanup (if they had cleanup logic)
    await asyncio.gather(*producer_tasks, return_exceptions=True)

    logging.info(f"Queue size at shutdown start: {broker.size}")
    logging.info("Waiting for queue to drain...")
    await broker.join()

    logging.info("Queue drained. Stopping consumers...")
    for task in consumer_tasks:
        task.cancel()
    await asyncio.gather(*consumer_tasks, return_exceptions=True)

    # Statistics
    total_produced = sum(p.messages_produced for p in producers)
    total_consumed = sum(c.messages_consumed for c in consumers)

    logging.info("-" * 30)
    logging.info("Simulation Report")
    logging.info("-" * 30)
    logging.info(f"Total Produced: {total_produced}")
    logging.info(f"Total Consumed: {total_consumed}")
    logging.info(f"Broker Empty:   {broker.is_empty}")
    logging.info("-" * 30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
