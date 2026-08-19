from src.config import LARGE_MODEL, SMALL_MODEL
from src.routing.router import route


def test_simple_question_routes_small_with_routing_on():
    decision = route("Where did Marie Curie study?", use_routing=True)
    assert decision.tier == "small"
    assert decision.model == SMALL_MODEL


def test_complex_question_routes_large_with_routing_on():
    decision = route(
        "Compare Marie Curie and Pierre Curie: how did their Nobel Prizes differ, and why?",
        use_routing=True,
    )
    assert decision.tier == "large"
    assert decision.model == LARGE_MODEL


def test_routing_disabled_always_routes_large():
    decision = route("Where did Marie Curie study?", use_routing=False)
    assert decision.tier == "large"
    assert decision.model == LARGE_MODEL


def test_decision_always_carries_the_underlying_score():
    decision = route("Where did Marie Curie study?", use_routing=False)
    assert 0.0 <= decision.score <= 1.0
