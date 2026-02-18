from __future__ import annotations

import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    - Lit X-Correlation-Id si fourni, sinon en génère un
    - Ajoute X-Correlation-Id à la réponse
    - (Traces détaillées par requête à l'étape 1)
    """

    header_name = "X-Correlation-Id"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        _ = time.time()
        cid = request.headers.get(self.header_name) or str(uuid.uuid4())
        request.state.correlation_id = cid

        response = await call_next(request)
        response.headers[self.header_name] = cid
        return response
