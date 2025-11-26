from fastapi import APIRouter

from .credentials import router as basic_auth_router
from .vk import router as vk_auth_router

__all__ = ("router",)

router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(basic_auth_router)
router.include_router(vk_auth_router)
