__all__ = ("router",)

from fastapi import APIRouter

from .collections import router as collections_router

router = APIRouter(prefix="/api/v1")

router.include_router(collections_router)
