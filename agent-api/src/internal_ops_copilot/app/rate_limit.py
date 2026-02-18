from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

log_quotas = logging.getLogger("quotas")


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_epoch: int


class FixedWindowRateLimiter:
    """
    Fixed window rate limiter.
    Stockage en mémoire.
    Horloge injectable pour tests déterministes.
    """

    def __init__(
        self,
        window_seconds: int,
        max_requests: int,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self._clock = clock or time.time
        self._store: dict[str, tuple[int, int]] = {}
        # key -> (window_start_epoch, count)

    def check(self, key: str) -> RateLimitResult:
        now = int(self._clock())
        window_start = now - (now % self.window_seconds)
        reset_epoch = window_start + self.window_seconds

        entry = self._store.get(key)
        if entry is None or entry[0] != window_start:
            self._store[key] = (window_start, 1)
            remaining = max(self.max_requests - 1, 0)
            return RateLimitResult(True, self.max_requests, remaining, reset_epoch)

        current_count = entry[1]
        if current_count >= self.max_requests:
            log_quotas.info("rate_limited", extra={"key": key})
            return RateLimitResult(False, self.max_requests, 0, reset_epoch)

        self._store[key] = (window_start, current_count + 1)
        remaining = max(self.max_requests - (current_count + 1), 0)
        return RateLimitResult(True, self.max_requests, remaining, reset_epoch)
