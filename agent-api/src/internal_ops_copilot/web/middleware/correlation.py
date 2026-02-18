from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    header_name = "X-Correlation-Id"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        _ = time.time()
        cid = request.headers.get(self.header_name) or str(uuid.uuid4())
        request.state.correlation_id = cid

        response = await call_next(request)
        response.headers[self.header_name] = cid
        return response
