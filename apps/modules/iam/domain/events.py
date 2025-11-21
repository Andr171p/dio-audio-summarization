from typing import ClassVar

from uuid import UUID

from pydantic import EmailStr

from modules.shared_kernel.domain import Event

from .value_objects import UserStatus


class UserRegisteredEvent(Event):
    event_type: ClassVar[str] = "user_registered"

    user_id: UUID
    user_status: UserStatus
    email: EmailStr
