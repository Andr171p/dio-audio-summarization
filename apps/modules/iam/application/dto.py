from uuid import UUID, uuid4

from pydantic import Field, PositiveFloat

from modules.shared_kernel.application import DTO
from modules.shared_kernel.utils import current_datetime


class TokenVerify(DTO):
    """Верификация токена"""

    token: str


class PKCESession(DTO):
    """PKCE сессия авторизации через OAuth2 flow"""

    session_id: UUID = Field(default_factory=uuid4)
    state: str
    code_verifier: str
    redirect_uri: str
    created_at: PositiveFloat = Field(default_factory=current_datetime().timestamp)


class VKCallback(DTO):
    """Callback для авторизации через VK"""

    authorization_code: str
    state: str
    device_id: str
