from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from internal_ops_copilot.app.config import get_settings
from internal_ops_copilot.app.rate_limit import FixedWindowRateLimiter

_settings = get_settings()


def _limiter_from_app(request: Request) -> FixedWindowRateLimiter:
    limiter = getattr(request.app.state, "rate_limiter", None)
    if limiter is None:
        # fallback sécurité si factory oublie l'init
        limiter = FixedWindowRateLimiter(
            window_seconds=_settings.rate_limit_window_seconds,
            max_requests=_settings.rate_limit_max_requests,
        )
        request.app.state.rate_limiter = limiter
    return limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not _settings.rate_limit_enabled:
            return await call_next(request)

        if not request.url.path.startswith("/v1"):
            return await call_next(request)

        api_key = request.headers.get(_settings.auth_api_key_header)
        if not api_key:
            # l'auth renverra 401
            return await call_next(request)

        limiter = _limiter_from_app(request)
        result = limiter.check(api_key)

        headers = {
            "RateLimit-Limit": str(result.limit),
            "RateLimit-Remaining": str(result.remaining),
            "RateLimit-Reset": str(result.reset_epoch),
        }

        if not result.allowed:
            headers["RateLimit-Remaining"] = "0"
            return JSONResponse(
                status_code=429,
                content={"error": {"code": "rate_limited", "message": "Too many requests"}},
                headers=headers,
            )

        response = await call_next(request)
        response.headers.update(headers)
        return response
