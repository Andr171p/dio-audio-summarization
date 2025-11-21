from fastapi import APIRouter

from .basic import router as basic_auth_router

__all__ = ("router",)

router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(basic_auth_router)
