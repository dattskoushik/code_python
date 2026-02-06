import asyncio
from typing import Optional
from .models import StreamPayload

class MessageBroker:
    """
    Asynchronous Message Broker utilizing a Priority Queue.
    Handles publishing and retrieval of StreamPayloads.
    """
    def __init__(self, maxsize: int = 100):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=maxsize)

    async def publish(self, message: StreamPayload, timeout: Optional[float] = None) -> bool:
        """
        Publishes a message to the queue.
        Returns True if successful, False if queue is full and timed out.
        """
        try:
            if timeout:
                 await asyncio.wait_for(self._queue.put(message), timeout)
            else:
                 await self._queue.put(message)
            return True
        except (asyncio.TimeoutError, asyncio.QueueFull):
            return False

    async def get_message(self) -> StreamPayload:
        """
        Retrieves a message from the queue. Waits indefinitely.
        """
        return await self._queue.get()

    def task_done(self):
        """
        Signals that a formerly enqueued task is complete.
        """
        self._queue.task_done()

    async def join(self):
        """
        Blocks until all items in the queue have been gotten and processed.
        """
        await self._queue.join()

    @property
    def size(self) -> int:
        return self._queue.qsize()

    @property
    def is_empty(self) -> bool:
        return self._queue.empty()

    @property
    def is_full(self) -> bool:
        return self._queue.full()
