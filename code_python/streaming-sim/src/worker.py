import asyncio
import random
import logging
from uuid import uuid4
from .models import StreamPayload
from .broker import MessageBroker

logger = logging.getLogger(__name__)

class Producer:
    def __init__(self, broker: MessageBroker, producer_id: str, interval: float = 1.0):
        self.broker = broker
        self.producer_id = producer_id
        self.interval = interval
        self.messages_produced = 0

    async def run(self):
        """
        Main loop for the producer.
        """
        logger.info(f"Producer {self.producer_id} started.")
        try:
            while True:
                # Random priority 1-10 (1 is highest)
                priority = random.randint(1, 10)
                payload = StreamPayload(
                    priority=priority,
                    event_type="sensor_reading",
                    payload={"value": random.random() * 100, "producer": self.producer_id}
                )

                # Try to publish with a short timeout to avoid blocking forever if queue is full
                success = await self.broker.publish(payload, timeout=0.1)
                if success:
                    self.messages_produced += 1
                    logger.debug(f"Producer {self.producer_id} produced msg {payload.id} (P{priority})")
                else:
                    logger.warning(f"Producer {self.producer_id} queue full, dropped message.")

                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            logger.info(f"Producer {self.producer_id} stopping...")
            raise

class Consumer:
    def __init__(self, broker: MessageBroker, consumer_id: str, processing_time: float = 0.5):
        self.broker = broker
        self.consumer_id = consumer_id
        self.processing_time = processing_time # simulated work
        self.messages_consumed = 0

    async def run(self):
        """
        Main loop for the consumer.
        """
        logger.info(f"Consumer {self.consumer_id} started.")
        try:
            while True:
                # Wait for next message
                msg = await self.broker.get_message()

                logger.debug(f"Consumer {self.consumer_id} picked up {msg.id} (P{msg.priority})")

                # Simulate blocking I/O or CPU work
                await asyncio.sleep(self.processing_time)

                self.messages_consumed += 1
                self.broker.task_done()
                logger.info(f"Consumer {self.consumer_id} finished {msg.id} (P{msg.priority})")

        except asyncio.CancelledError:
            logger.info(f"Consumer {self.consumer_id} stopping...")
            raise
