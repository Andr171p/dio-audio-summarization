from pydantic import BaseModel


class TokenVerify(BaseModel):
    """Верификация токена"""
    token: str
