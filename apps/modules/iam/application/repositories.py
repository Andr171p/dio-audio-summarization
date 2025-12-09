from abc import abstractmethod

from pydantic import EmailStr

from modules.shared_kernel.application import CRUDRepository

from ..domain import AnyUser, AuthProvider, Guest, User


class UserRepository(CRUDRepository[AnyUser]):
    @abstractmethod
    async def get_by_device_id(self, device_id: str) -> Guest | None: ...

    @abstractmethod
    async def get_by_email(self, email: EmailStr) -> User | None: ...

    @abstractmethod
    async def get_by_social_account(
            self, provider: AuthProvider, social_user_id: str
    ) -> User | None: ...
