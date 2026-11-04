"""Request correlation, access logging and Prometheus metrics."""

import logging
import time
import uuid
from contextvars import ContextVar

from prometheus_client import Counter, Histogram
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

request_id_context: ContextVar[str] = ContextVar("request_id", default="-")
logger = logging.getLogger("app.access")

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["method", "path"],
)

REQUEST_ID_HEADER = "X-Request-ID"
_MAX_REQUEST_ID_LENGTH = 128


def current_request_id() -> str:
    """Request id of the task being executed, for log correlation."""
    return request_id_context.get()


def _read_request_id(scope: Scope) -> str:
    for name, value in scope.get("headers", []):
        if name.lower() == b"x-request-id":
            candidate = value.decode("latin-1").strip()
            if candidate and len(candidate) <= _MAX_REQUEST_ID_LENGTH:
                return candidate
    return uuid.uuid4().hex


class RequestContextMiddleware:
    """Assign a request id, emit an access log line and record metrics."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _read_request_id(scope)
        scope.setdefault("state", {})["request_id"] = request_id

        method = scope.get("method", "GET")
        start = time.perf_counter()
        status_code = 500
        token = request_id_context.set(request_id)

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = MutableHeaders(scope=message)
                headers[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.perf_counter() - start
            route = scope.get("route")
            path = getattr(route, "path", scope.get("path", "unknown"))
            REQUEST_COUNT.labels(method=method, path=path, status=str(status_code)).inc()
            REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
            logger.info(
                "%s %s -> %d in %.1fms",
                method,
                scope.get("path", ""),
                status_code,
                duration * 1000,
            )
            request_id_context.reset(token)
