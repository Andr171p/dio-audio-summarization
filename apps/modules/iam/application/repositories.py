from abc import abstractmethod

from pydantic import EmailStr

from modules.shared_kernel.application import CRUDRepository

from ..domain import AuthProvider, User


class UserRepository(CRUDRepository[User]):
    @abstractmethod
    async def get_by_email(self, email: EmailStr) -> User | None: ...

    @abstractmethod
    async def get_by_social_account(self, provider: AuthProvider, user_id: str) -> User | None: ...
