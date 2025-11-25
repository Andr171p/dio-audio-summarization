__all__ = ("router",)

from fastapi import APIRouter

from .basic import router as basic_registration_router
from .vk import router as vk_registration_router

router = APIRouter(tags=["Registration"])

router.include_router(basic_registration_router)
router.include_router(vk_registration_router)
