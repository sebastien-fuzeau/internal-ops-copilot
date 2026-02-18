from __future__ import annotations

import logging

from fastapi import FastAPI

from internal_ops_copilot.app.config import get_settings
from internal_ops_copilot.app.logging_config import LoggingConfig, configure_logging
from internal_ops_copilot.web.middleware.correlation import CorrelationIdMiddleware
from internal_ops_copilot.web.routes.health import router as health_router

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

    # Middleware
    app.add_middleware(CorrelationIdMiddleware)

    # Routes (versioning à l'étape suivante; ici base health)
    app.include_router(health_router)

    log.info("app_started", extra={"status_code": 0})
    return app
