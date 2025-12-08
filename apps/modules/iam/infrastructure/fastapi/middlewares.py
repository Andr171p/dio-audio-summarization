from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class AnonymousMiddleware(BaseHTTPMiddleware):
    """Middleware для автоматического создания анонимного пользователя
    при первом посещении приложения
    """

    def __init__(
            self, app: ASGIApp, *, exclude_paths: list[str] | None = None
    ) -> None:
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs", "/redoc", "/openapi.json",
            "/static/", "/favicon.ico", "/health"
        ]

    def _should_skip_request(self, request: Request) -> bool:
        """Нужно ли пропустить запрос"""

        path = request.url.path
        for excluded_path in self.exclude_paths:
            if path.startswith(excluded_path):
                return True
        return request.method == "OPTIONS"

    async def _get_or_create_anonymous_user(self, request: Request) -> ...: ...

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if self._should_skip_request(request):
            return await call_next(request)
        return ...
