from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from internal_ops_copilot.web.middleware.correlation import CORRELATION_HEADER

TRACE_HEADER = "X-Trace-Id"

log_api = logging.getLogger("api")


class TracingMiddleware(BaseHTTPMiddleware):
    """
    Tracing minimal "prod" :
    - génère un trace_id par requête
    - mesure durée + status_code
    - émet 1 log JSON "request_end" avec champs structurés
    - ajoute X-Trace-Id à la réponse
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()

        trace_id = request.headers.get(TRACE_HEADER) or str(uuid.uuid4())
        request.state.trace_id = trace_id

        try:
            response = await call_next(request)
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)

            correlation_id = getattr(request.state, "correlation_id", None) or request.headers.get(
                CORRELATION_HEADER
            )

            status_code = getattr(getattr(request, "state", None), "status_code", None)
            # status_code réel: si on a une Response, on le loggue via response (voir plus bas)
            # (le finally s'exécute même si call_next lève; on loggue au mieux)

            log_api.info(
                "request_end",
                extra={
                    "correlation_id": correlation_id,
                    "trace_id": trace_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "status_code": getattr(
                        locals().get("response", None), "status_code", status_code
                    ),
                },
            )

        # si call_next a levé, on ne peut pas ajouter le header; FastAPI gérera l’exception
        response.headers[TRACE_HEADER] = trace_id
        return response
