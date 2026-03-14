"""
Background worker module.

Provides a task registry and two submission paths:
  - submit()        — sync contexts (runs task in a daemon thread)
  - submit_async()  — async contexts (runs task in asyncio thread pool)

Both paths persist job state to the `jobs` table in Supabase so every
background execution is observable via the /api/jobs endpoints.

Usage
-----
# Register a task (typically done at import time in the owning module):
from worker import register_task

@register_task("my_task")
def my_task(arg1, arg2):
    ...
    return {"status": "done"}

# Submit from a sync context:
from worker import submit
job_id = submit("my_task", {"arg1": "hello", "arg2": 42}, organization_id=org_id)

# Submit from an async context:
from worker import submit_async
job_id = await submit_async("my_task", {"arg1": "hello", "arg2": 42})
"""

import asyncio
import threading
from typing import Any, Callable, Dict, Optional

# ── Task registry ──────────────────────────────────────────────────────────────

_REGISTRY: Dict[str, Callable] = {}


def register_task(name: str) -> Callable:
    """Decorator: register a callable as a named background task."""
    def decorator(fn: Callable) -> Callable:
        _REGISTRY[name] = fn
        return fn
    return decorator


# ── Sync submission (daemon thread) ────────────────────────────────────────────

def submit(
    task_type: str,
    payload: Dict[str, Any],
    organization_id: str = None
) -> str:
    """
    Submit a task from a synchronous context.
    Creates a DB job record, then runs the task in a daemon thread.
    Returns the job_id immediately (non-blocking).
    """
    from db import create_job, update_job_status

    job_id = create_job(task_type, payload, organization_id)

    fn = _REGISTRY.get(task_type)
    if fn is None:
        update_job_status(job_id, "failed", error=f"Unknown task type: {task_type}")
        return job_id

    def _run():
        update_job_status(job_id, "running")
        try:
            result = fn(**payload)
            update_job_status(job_id, "done", result=result or {})
        except Exception as e:
            print(f"[worker] {task_type} failed: {e}")
            update_job_status(job_id, "failed", error=str(e))

    threading.Thread(target=_run, daemon=True).start()
    return job_id


# ── Async submission (asyncio thread pool) ─────────────────────────────────────

async def submit_async(
    task_type: str,
    payload: Dict[str, Any],
    organization_id: str = None
) -> str:
    """
    Submit a task from an async context.
    Creates a DB job record, then schedules the task as an asyncio background task.
    Returns the job_id immediately (non-blocking).
    """
    from db import create_job, update_job_status

    job_id = create_job(task_type, payload, organization_id)

    fn = _REGISTRY.get(task_type)
    if fn is None:
        update_job_status(job_id, "failed", error=f"Unknown task type: {task_type}")
        return job_id

    async def _run():
        update_job_status(job_id, "running")
        try:
            if asyncio.iscoroutinefunction(fn):
                result = await fn(**payload)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: fn(**payload))
            update_job_status(job_id, "done", result=result or {})
        except Exception as e:
            print(f"[worker] {task_type} failed: {e}")
            update_job_status(job_id, "failed", error=str(e))

    asyncio.create_task(_run())
    return job_id
