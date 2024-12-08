from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.db import DbConfig


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


# todo: Поднимаемся на 1 уровень вверх где лежит .env
BASE_PATH = Path(__file__).resolve().parent.parent


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=(
            BASE_PATH / ".env.local.base",
            BASE_PATH / ".env.local",
            BASE_PATH / ".env",
        ),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
    )
    db: DbConfig = DbConfig()
    kafka: KafkaConfig = KafkaConfig()
    sentry_dsn: str | None = None
    tg: TGConfig = TGConfig()
    cors_origin_regex: str = (
        r"(http://|https://)?(.*\.)?(qa|stage|localhost|0.0.0.0)(\.ru)?(:\d+)?$"
    )


APP_CONFIG = AppConfig()
