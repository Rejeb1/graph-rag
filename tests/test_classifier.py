from src.routing.classifier import complexity_score


def test_empty_question_scores_zero():
    assert complexity_score("") == 0.0
    assert complexity_score("   ") == 0.0


def test_simple_question_scores_low():
    score = complexity_score("Where did Marie Curie study?")
    assert 0.0 < score < 0.5


def test_comparative_question_scores_higher_than_simple():
    simple = complexity_score("Where did Marie Curie study?")
    comparative = complexity_score(
        "Compare Marie Curie and Pierre Curie: how did their Nobel Prizes differ, and why?"
    )
    assert comparative > simple


def test_marker_phrase_raises_score():
    without = complexity_score("Marie Curie discovered radium.")
    with_marker = complexity_score("Explain why Marie Curie discovered radium.")
    assert with_marker > without


def test_score_is_bounded_between_zero_and_one():
    long_question = "why " * 100 + "compare relationship between path between trace connect"
    assert 0.0 <= complexity_score(long_question) <= 1.0


def test_multiple_capitalized_entities_raise_score():
    one_entity = complexity_score("who is marie?")
    two_entities = complexity_score("How are Marie Curie and Pierre Curie related?")
    assert two_entities > one_entity
