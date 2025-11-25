from pydantic import BaseModel


class TokenVerify(BaseModel):
    """Верификация токена"""

    token: str


class OAuthSession(BaseModel):
    """Сессия авторизации через OAuth2 flow"""

    state: str
    code_verifier: str


class VKCallback(BaseModel):
    """Callback для авторизации через VK"""

    authorization_code: str
    state: str
    device_id: str
