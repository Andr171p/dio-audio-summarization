from typing import Final

import logging

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from modules.shared_kernel.domain import AppError, ErrorType

from .container import container
from .v1.routers import router

logger = logging.getLogger(__name__)


def create_fastapi_app() -> FastAPI:
    app = FastAPI(title="DIO audio summarization API")
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    setup_dishka(app=app, container=container)
    return app


# Маппинг доменных ошибок к HTTP статус кодам
HTTP_STATUS_CODE_MAP: Final[dict[ErrorType, int]] = {
    ErrorType.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorType.CONFLICT: status.HTTP_409_CONFLICT,
    ErrorType.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorType.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
    ErrorType.RATE_LIMITED: status.HTTP_429_TOO_MANY_REQUESTS,
    ErrorType.PRECONDITION_FAILED: status.HTTP_412_PRECONDITION_FAILED,
    ErrorType.INVARIANT_VIOLATION: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorType.EXTERNAL_DEPENDENCY_ERROR: status.HTTP_502_BAD_GATEWAY,
    ErrorType.UNKNOWN: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(ValidationError)
    def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
        logger.error(exc)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=exc.errors())

    @app.exception_handler(AppError)
    def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.error(exc)
        return JSONResponse(status_code=HTTP_STATUS_CODE_MAP[exc.type], content=exc.to_dict())


app: Final[FastAPI] = create_fastapi_app()
