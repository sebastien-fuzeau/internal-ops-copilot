from __future__ import annotations

import logging

from fastapi import FastAPI

from internal_ops_copilot.app.config import get_settings
from internal_ops_copilot.app.logging_config import LoggingConfig, configure_logging
from internal_ops_copilot.app.rate_limit import FixedWindowRateLimiter
from internal_ops_copilot.web.middleware.correlation import CorrelationIdMiddleware
from internal_ops_copilot.web.middleware.rate_limit import RateLimitMiddleware
from internal_ops_copilot.web.middleware.tracing import TracingMiddleware
from internal_ops_copilot.web.routes.health import router as health_router
from internal_ops_copilot.web.routes.v1.meta import router as v1_meta_router

log = logging.getLogger("main")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(LoggingConfig(level=settings.log_level, fmt=settings.log_format))

    app = FastAPI(
        title="Internal Ops Copilot API",
        version="0.0.1",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # State (évite fuite inter-tests)
    app.state.rate_limiter = FixedWindowRateLimiter(
        window_seconds=settings.rate_limit_window_seconds,
        max_requests=settings.rate_limit_max_requests,
    )

    # Middleware
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(TracingMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Routes
    app.include_router(health_router)  # /healthz /readyz restent root
    app.include_router(v1_meta_router)  # /v1/ping

    log.info("app_started", extra={"status_code": 0})
    return app
