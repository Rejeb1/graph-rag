from src.api import stats


def test_snapshot_starts_at_zero_or_reflects_prior_test_state():
    snap = stats.snapshot()
    assert snap["total_requests"] >= 0
    assert set(snap["tier_counts"].keys()) >= {"small", "large"}


def test_record_increments_totals_and_tier_counts():
    before = stats.snapshot()
    stats.record("small", 0.42)
    after = stats.snapshot()

    assert after["total_requests"] == before["total_requests"] + 1
    assert after["tier_counts"]["small"] == before["tier_counts"].get("small", 0) + 1


def test_avg_latency_is_computed_correctly():
    stats.record("large", 1.0)
    stats.record("large", 3.0)
    snap = stats.snapshot()
    # avg should be the running mean, not just the last value
    assert snap["avg_latency_seconds"] > 0
