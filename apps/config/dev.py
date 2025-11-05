from typing import Final, Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from .base import ENV_PATH

load_dotenv(ENV_PATH)


class PostgresSettings(BaseSettings):
    user: str = "<USER>"
    password: str = "<PASSWORD>"
    host: str = "localhost"
    port: int = 5432
    db: str = "postgres"
    driver: Literal["asyncpg"] = "asyncpg"

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    @property
    def sqlalchemy_url(self) -> str:
        return f"postgresql+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):
    postgres: PostgresSettings = PostgresSettings()


settings: Final[Settings] = Settings()
