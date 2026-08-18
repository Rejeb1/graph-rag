"""Route a question to the small (Groq) or large (Claude) model."""

from dataclasses import dataclass

from src.config import LARGE_MODEL, ROUTING_THRESHOLD, SMALL_MODEL
from src.routing.classifier import complexity_score


@dataclass
class RoutingDecision:
    model: str
    tier: str  # "small" | "large"
    score: float


def route(question: str, use_routing: bool = True, threshold: float = ROUTING_THRESHOLD) -> RoutingDecision:
    """`use_routing=False` forces the large model — used by the Bloc 3 benchmark
    as the no-routing baseline to measure routing's cost/latency tradeoff."""
    score = complexity_score(question)
    if use_routing and score < threshold:
        return RoutingDecision(model=SMALL_MODEL, tier="small", score=score)
    return RoutingDecision(model=LARGE_MODEL, tier="large", score=score)
