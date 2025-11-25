__all__ = ("router",)

from fastapi import APIRouter

from .auth import router as auth_router
from .collections import router as collections_router
from .registration import router as registration_router
from .summaries import router as summaries_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(collections_router)
router.include_router(summaries_router)
router.include_router(registration_router)
