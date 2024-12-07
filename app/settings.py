import os
from pathlib import Path

from pydantic import BaseModel
from pyhocon import ConfigFactory

from app.utils.db import DbConfig


class TGConfig(BaseModel):
    token: str = ""
    chat_id: str = ""


class KafkaConfig(BaseModel):
    host: str
    port: int
    batch_size: int = 5
    topik: str = "default"

    @property
    def bootstrap_servers(self) -> str:
        return f"{self.host}:{self.port}"


class AppConfig(BaseModel):
    bd: DbConfig
    kafka: KafkaConfig
    sentry_dsn: str | None = None
    tg: TGConfig = TGConfig()
    cors_origin_regex: str

    @classmethod
    def create(cls) -> "AppConfig":
        env = os.getenv("ENV", "base")
        path = Path(__file__).parent / "settings"
        config_factory = ConfigFactory.parse_file(path / f"{env}.conf")
        config_factory = config_factory.with_fallback(path / "base.conf")
        return cls(**dict(config_factory))


APP_CONFIG = AppConfig.create()
