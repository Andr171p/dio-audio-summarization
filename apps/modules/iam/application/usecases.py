from modules.shared_kernel.application import MessageBus

from ..domain import CredentialsRegistration, User
from .exceptions import AlreadyRegisteredError
from .repositories import UserRepository


class CredentialsRegistrationUseCase:
    """Регистрация пользователя через учётные данные"""

    def __init__(self, repository: UserRepository, message_bus: MessageBus) -> None:
        self._repository = repository
        self._message_bus = message_bus

    async def execute(self, registration: CredentialsRegistration) -> User:
        user = await self._repository.get_by_email(registration.email)
        if user is None:
            user = User.register(registration)
            await self._repository.create(user)
        elif user is not None and not user.is_registration_completed():
            user.repeat_email_verification()
        else:
            raise AlreadyRegisteredError(
                f"User with email {user.email} already registered",
                details={"email": user.email, "username": user.username}
            )
        for event in user.collect_events():
            await self._message_bus.send(event)
        return user
