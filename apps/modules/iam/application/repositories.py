from abc import abstractmethod

from pydantic import EmailStr

from modules.shared_kernel.application import CRUDRepository

from ..domain import User


class UserRepository(CRUDRepository[User]):
    @abstractmethod
    async def get_by_email(self, email: EmailStr) -> User | None: ...
