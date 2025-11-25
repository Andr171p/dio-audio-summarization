from modules.shared_kernel.application import MessageBus, UnitOfWork

from ..domain import User, UserCredentials
from .exceptions import AlreadyRegisteredError
from .repositories import UserRepository


class RegisterByCredentialsUseCase:
    """Регистрация пользователя через учётные данные"""

    def __init__(
            self, uow: UnitOfWork, repository: UserRepository, message_bus: MessageBus
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._message_bus = message_bus

    async def execute(self, credentials: UserCredentials) -> User:
        async with self._uow.transactional() as uow:
            user = await self._repository.get_by_email(credentials.email)
            if user is None:
                user = User.register_by_credentials(credentials)
                await self._repository.create(user)
            elif user is not None and not user.is_registration_completed():
                user.repeat_email_verification()
            else:
                raise AlreadyRegisteredError(
                    f"User with email {user.email} already registered",
                    details={"email": user.email, "username": user.username}
                )
            await uow.commit()
            for event in user.collect_events():
                await self._message_bus.send(event)
            return user
