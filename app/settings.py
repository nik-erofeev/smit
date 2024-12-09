import os
from enum import StrEnum, unique

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.db import DbConfig


@unique
class Environments(StrEnum):
    local = "local"
    qa = "qa"
    stage = "stage"
    prod = "prod"
    test = "test"


class TGConfig(BaseModel):
    token: str = ""
    chat_id: str = ""


class KafkaConfig(BaseModel):
    host: str = ""
    port: int = 9092
    batch_size: int = 5
    topik: str = "default"

    @property
    def bootstrap_servers(self) -> str:
        return f"{self.host}:{self.port}"


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=(".env.local.base", ".env.local", ".env"),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
    )

    environment: Environments = Environments.local
    db: DbConfig = DbConfig()
    kafka: KafkaConfig = KafkaConfig()
    sentry_dsn: str | None = None
    tg: TGConfig = TGConfig()
    cors_origin_regex: str = (
        r"(http://|https://)?(.*\.)?(qa|stage|localhost|0.0.0.0)(\.ru)?(:\d+)?$"
    )


#  Поднимаемся на 1 уровень вверх где лежит .env
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

APP_CONFIG = AppConfig()
