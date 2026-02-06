import pytest
import asyncio
import sys
import os

# Ensure project root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import StreamPayload
from src.broker import MessageBroker
from src.worker import Producer, Consumer

# Test Priority Logic
def test_payload_priority():
    # Priority 1 is higher than 10
    high_p = StreamPayload(priority=1, event_type="test", payload={})
    low_p = StreamPayload(priority=10, event_type="test", payload={})

    assert high_p < low_p
    # Check that sorting works as expected (Ascending order of priority value)
    l = [low_p, high_p]
    l.sort()
    assert l[0] == high_p

@pytest.mark.asyncio
async def test_broker_publish_consume():
    broker = MessageBroker(maxsize=5)
    payload = StreamPayload(priority=5, event_type="test", payload={})

    success = await broker.publish(payload)
    assert success is True
    assert broker.size == 1

    msg = await broker.get_message()
    assert msg.id == payload.id
    broker.task_done()
    assert broker.size == 0

@pytest.mark.asyncio
async def test_broker_backpressure():
    broker = MessageBroker(maxsize=1)
    payload = StreamPayload(priority=5, event_type="test", payload={})

    await broker.publish(payload)

    # Next publish should timeout
    success = await broker.publish(payload, timeout=0.1)
    assert success is False

@pytest.mark.asyncio
async def test_priority_ordering():
    broker = MessageBroker(maxsize=10)
    low = StreamPayload(priority=10, event_type="test", payload={})
    high = StreamPayload(priority=1, event_type="test", payload={})
    med = StreamPayload(priority=5, event_type="test", payload={})

    await broker.publish(low)
    await broker.publish(high)
    await broker.publish(med)

    # Should come out: High, Med, Low
    msg1 = await broker.get_message()
    assert msg1.priority == 1
    broker.task_done()

    msg2 = await broker.get_message()
    assert msg2.priority == 5
    broker.task_done()

    msg3 = await broker.get_message()
    assert msg3.priority == 10
    broker.task_done()

@pytest.mark.asyncio
async def test_end_to_end():
    broker = MessageBroker(maxsize=10)
    producer = Producer(broker, "TestProducer", interval=0.01)
    consumer = Consumer(broker, "TestConsumer", processing_time=0.01)

    p_task = asyncio.create_task(producer.run())
    c_task = asyncio.create_task(consumer.run())

    await asyncio.sleep(0.1)

    p_task.cancel()
    try:
        await p_task
    except asyncio.CancelledError:
        pass

    await broker.join()
    c_task.cancel()
    try:
        await c_task
    except asyncio.CancelledError:
        pass

    assert producer.messages_produced > 0
    assert consumer.messages_consumed >= producer.messages_produced
