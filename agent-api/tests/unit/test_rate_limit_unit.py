from internal_ops_copilot.app.rate_limit import FixedWindowRateLimiter


def test_fixed_window_basic() -> None:
    fake_time = [1000]

    def clock() -> float:
        return fake_time[0]

    limiter = FixedWindowRateLimiter(window_seconds=60, max_requests=2, clock=clock)

    r1 = limiter.check("key1")
    assert r1.allowed
    assert r1.remaining == 1

    r2 = limiter.check("key1")
    assert r2.allowed
    assert r2.remaining == 0

    r3 = limiter.check("key1")
    assert not r3.allowed

    # Avance fenêtre
    fake_time[0] += 60

    r4 = limiter.check("key1")
    assert r4.allowed
    assert r4.remaining == 1
