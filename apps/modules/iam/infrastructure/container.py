from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.shared_kernel.application import UnitOfWork
from modules.shared_kernel.application.message_bus import LogMessageBus

from ..application import CredentialsAuthNService, RegisterByCredentialsUseCase, UserRepository
from .database import SQLAlchemyUserRepository


class IAMProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_user_repo(self, session: AsyncSession) -> UserRepository:  # noqa: PLR6301
        return SQLAlchemyUserRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_credentials_registration_usecase(  # noqa: PLR6301
            self, uow: UnitOfWork, user_repo: UserRepository
    ) -> RegisterByCredentialsUseCase:
        return RegisterByCredentialsUseCase(
            uow=uow, repository=user_repo, message_bus=LogMessageBus()
        )

    @provide(scope=Scope.REQUEST)
    def provide_credentials_authn_service(  # noqa: PLR6301
            self, user_repo: UserRepository
    ) -> CredentialsAuthNService:
        return CredentialsAuthNService(user_repo)
