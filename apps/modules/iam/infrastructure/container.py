from datetime import timedelta

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from config.dev import settings
from modules.shared_kernel.application import KeyValueCache, UnitOfWork
from modules.shared_kernel.application.message_bus import LogMessageBus

from ..application import CredentialsAuthService, GuestService, UserRepository, VKAuthService
from ..application.dto import PKCESession
from .cache import PKCESessionCache
from .database import SQLAlchemyUserRepository


class IAMProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_user_repo(self, session: AsyncSession) -> UserRepository:  # noqa: PLR6301
        return SQLAlchemyUserRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_guest_service(self, uow: UnitOfWork, user_repo: UserRepository) -> GuestService:  # noqa: PLR6301
        return GuestService(uow=uow, repository=user_repo)

    @provide(scope=Scope.APP)
    def provide_pkce_session_cache(self) -> KeyValueCache[PKCESession]:  # noqa: PLR6301
        return PKCESessionCache(
            url=settings.redis.url,
            prefix="pkce",
            ttl=timedelta(minutes=settings.oauth.pkce_session_expires_in_minutes)
        )

    @provide(scope=Scope.REQUEST)
    def provide_credentials_auth_service(  # noqa: PLR6301
            self, uow: UnitOfWork, user_repo: UserRepository
    ) -> CredentialsAuthService:
        return CredentialsAuthService(
            uow=uow, repository=user_repo, message_bus=LogMessageBus()
        )

    @provide(scope=Scope.REQUEST)
    def provide_vk_auth_service(  # noqa: PLR6301
            self, uow: UnitOfWork, user_repo: UserRepository, cache: KeyValueCache[PKCESession]
    ) -> VKAuthService:
        return VKAuthService(
            uow=uow, repository=user_repo, cache=cache, message_bus=LogMessageBus()
        )
