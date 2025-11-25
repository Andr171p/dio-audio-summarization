__all__ = (
    "vk_oauth_client",
)

from config.dev import settings

from .vk import VKOAuthClient

vk_oauth_client = VKOAuthClient(
    client_id=settings.vk.client_id,
    base_url=settings.vk.base_url,
    redirect_uri=settings.vk.redirect_uri
)
