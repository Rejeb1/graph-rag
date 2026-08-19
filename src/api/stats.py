"""In-memory request stats, exposed via GET /stats.

Resets on restart/redeploy — this is a lightweight observability signal for
a demo instance, not a durable metrics store. For anything beyond that,
point the structured log lines (see main.py) at a real log aggregator.
"""

import threading
from dataclasses import dataclass, field


@dataclass
class _Stats:
    total_requests: int = 0
    tier_counts: dict[str, int] = field(default_factory=lambda: {"small": 0, "large": 0})
    total_latency_seconds: float = 0.0


_lock = threading.Lock()
_stats = _Stats()


def record(tier: str, latency_seconds: float) -> None:
    with _lock:
        _stats.total_requests += 1
        _stats.tier_counts[tier] = _stats.tier_counts.get(tier, 0) + 1
        _stats.total_latency_seconds += latency_seconds


def snapshot() -> dict:
    with _lock:
        avg_latency = round(_stats.total_latency_seconds / _stats.total_requests, 3) if _stats.total_requests else 0.0
        return {
            "total_requests": _stats.total_requests,
            "tier_counts": dict(_stats.tier_counts),
            "avg_latency_seconds": avg_latency,
        }
