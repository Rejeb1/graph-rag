import pytest
from fastapi import HTTPException

from src.api.rate_limit import MAX_REQUESTS_PER_WINDOW, rate_limit


class _FakeClient:
    def __init__(self, host: str) -> None:
        self.host = host


class _FakeRequest:
    def __init__(self, host: str) -> None:
        self.client = _FakeClient(host)


def test_requests_within_the_limit_are_allowed():
    request = _FakeRequest("10.0.0.1")
    for _ in range(MAX_REQUESTS_PER_WINDOW):
        rate_limit(request)  # should not raise


def test_exceeding_the_limit_raises_429():
    request = _FakeRequest("10.0.0.2")
    for _ in range(MAX_REQUESTS_PER_WINDOW):
        rate_limit(request)
    with pytest.raises(HTTPException) as exc_info:
        rate_limit(request)
    assert exc_info.value.status_code == 429


def test_different_ips_have_independent_limits():
    request_a = _FakeRequest("10.0.0.3")
    request_b = _FakeRequest("10.0.0.4")
    for _ in range(MAX_REQUESTS_PER_WINDOW):
        rate_limit(request_a)
    # a different IP should still be allowed even though A is now exhausted
    rate_limit(request_b)


def test_missing_client_falls_back_to_unknown_bucket():
    request = _FakeRequest.__new__(_FakeRequest)
    request.client = None
    rate_limit(request)  # should not raise (uses "unknown" bucket)
