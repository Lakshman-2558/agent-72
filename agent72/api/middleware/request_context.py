"""Request Context and Observability Middleware."""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from agent72.core.logging import get_logger

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware attaching request IDs and timing to every incoming HTTP request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-MS"] = str(duration_ms)

        # Skip spamming logs for health polls unless error
        if not request.url.path.startswith("/api/v1/health") or response.status_code >= 400:
            logger.info(
                f"{request.method} {request.url.path} "
                f"status={response.status_code} duration={duration_ms}ms request_id={request_id}"
            )

        return response
