import asyncio
import logging
from typing import Any, Dict, Callable

logger = logging.getLogger(__name__)

# Registry to hold task handlers
TASK_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

def register_task(name: str):
    """Decorator to register a task handler."""
    def decorator(func):
        TASK_REGISTRY[name] = func
        return func
    return decorator

@register_task("math_op")
async def task_math_op(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Performs basic math operations."""
    operation = payload.get("operation")
    a = payload.get("a")
    b = payload.get("b")

    await asyncio.sleep(0.5)  # Simulate CPU work

    if operation == "add":
        return {"result": a + b}
    elif operation == "multiply":
        return {"result": a * b}
    else:
        raise ValueError(f"Unknown operation: {operation}")

@register_task("text_reverse")
async def task_text_reverse(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Reverses the input text."""
    text = payload.get("text", "")
    await asyncio.sleep(0.5)
    return {"result": text[::-1]}

@register_task("mock_api_fetch")
async def task_mock_api(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Simulates an external API call."""
    url = payload.get("url")
    logger.info(f"Fetching {url}...")
    await asyncio.sleep(2.0)  # Simulate network latency
    return {"status": 200, "data": f"Mock data for {url}"}

async def execute_task(task_type: str, payload: Dict[str, Any]) -> Any:
    handler = TASK_REGISTRY.get(task_type)
    if not handler:
        raise ValueError(f"No handler registered for task type: {task_type}")

    if asyncio.iscoroutinefunction(handler):
        return await handler(payload)
    else:
        return handler(payload)
