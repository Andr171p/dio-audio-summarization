__all__ = ("router",)

from .chats import router
from .messages import router as messages_router

router.include_router(messages_router)
