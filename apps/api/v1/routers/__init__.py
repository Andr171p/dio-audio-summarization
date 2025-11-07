__all__ = ("router",)

from fastapi import APIRouter

from .collections import router as collections_router
from .summaries import router as summaries_router

router = APIRouter(prefix="/api/v1")

router.include_router(collections_router)
router.include_router(summaries_router)
