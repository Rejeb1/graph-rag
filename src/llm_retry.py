"""Retry helper for Groq's strict JSON-schema mode, which occasionally
returns an empty completion under load (observed: `json_validate_failed`
with `failed_generation: ''`, not reproducible on retry) — not caught by the
SDK's own retry logic, which only covers 429/5xx, not this 400."""

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def call_with_retries(fn: Callable[[], T], retries: int = 2, delay: float = 1.0) -> T:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - deliberately broad, see module docstring
            last_exc = exc
            if attempt < retries:
                time.sleep(delay)
    assert last_exc is not None
    raise last_exc
