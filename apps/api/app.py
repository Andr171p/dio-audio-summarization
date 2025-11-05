from typing import Final

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .container import container
from .v1.routers import router


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
    setup_dishka(app=app, container=container)
    return app


app: Final[FastAPI] = create_fastapi_app()
