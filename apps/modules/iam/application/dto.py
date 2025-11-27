from uuid import UUID, uuid4

from pydantic import EmailStr, Field, PositiveFloat

from modules.iam.domain import UserRole, UserStatus
from modules.shared_kernel.application import DTO
from modules.shared_kernel.utils import current_datetime


class TokenVerify(DTO):
    """Верификация токена"""

    token: str


class OAuthFlowInit(DTO):
    """Инициированный поток OAuth 2.0"""

    authorization_url: str
    pkce_session_id: str


class PKCESession(DTO):
    """PKCE сессия авторизации через OAuth2 flow"""

    session_id: UUID = Field(default_factory=uuid4)
    state: str
    code_verifier: str
    created_at: PositiveFloat = Field(default_factory=current_datetime().timestamp)


class VKCallback(DTO):
    """Callback для авторизации через VK"""

    authorization_code: str
    state: str
    device_id: str


class CurrentUser(DTO):
    """Авторизованный пользователь, который делает запрос"""

    user_id: UUID
    username: str | None = None
    email: EmailStr | None = None
    status: UserStatus
    role: UserRole
