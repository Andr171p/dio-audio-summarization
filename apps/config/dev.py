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


class MinioSettings(BaseSettings):
    url: str = "<URL>"
    user: str = "<USER>"
    password: str = "<PASSWORD>"
    bucket: str = "dev"

    model_config = SettingsConfigDict(env_prefix="MINIO_")


class RabbitMQSettings(BaseSettings):
    user: str = "<USER>"
    password: str = "<PASSWORD>"
    host: str = "localhost"
    port: int = 5672

    model_config = SettingsConfigDict(env_prefix="RABBITMQ_")

    @property
    def url(self) -> str:
        return ...


class SaluteSpeechSettings(BaseSettings):
    apikey: str = "<APIKEY>"
    scope: str = "<SCOPE>"
    client_id: str = "<CLIENT_ID>"
    client_secret: str = "<CLIENT_SECRET>"

    model_config = SettingsConfigDict(env_prefix="SALUTE_SPEECH")


class AppSettings(BaseSettings):
    port: int = 8000
    host: str = "localhost"
    title: str = "<TITLE>"
    version: str = "0.1.0"

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    postgres: PostgresSettings = PostgresSettings()
    minio: MinioSettings = MinioSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    salute_speech: SaluteSpeechSettings = SaluteSpeechSettings()


settings: Final[Settings] = Settings()
