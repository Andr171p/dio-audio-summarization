from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from ...application import GuestService
from ...application.queries import GetGuestQuery


class GuestMiddleware(BaseHTTPMiddleware):
    """Middleware для автоматического создания/восстановления гостя"""

    def __init__(
            self, app: ASGIApp, service: GuestService, exclude_paths: list[str] | None = None
    ) -> None:
        super().__init__(app)
        self.service = service
        self.exclude_paths = exclude_paths or [
            "/docs", "/redoc", "/openapi.json", "/health", "/metrics"
        ]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        query = GetGuestQuery.model_validate({
            "guest_id": request.headers.get("X-Guest-ID"),
            "devise_id": request.headers.get("X-Device-ID"),
        })
        token = await self.service.get_or_create(query)
        response = await call_next(request)
        response.headers["X-Guest-ID"] = str(token.guest_id)
        response.headers["Authorization"] = f"Bearer {token.access_token}"
        return response
