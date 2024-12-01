import os
from pathlib import Path

from pydantic import BaseModel
from pyhocon import ConfigFactory  # type: ignore

from app.utils.db import DbConfig


class KafkaConfig(BaseModel):
    host: str
    port: int
    batch_size: int = 2

    @property
    def bootstrap_servers(self) -> str:
        return f"{self.host}:{self.port}"


class AppConfig(BaseModel):
    bd: DbConfig
    kafka: KafkaConfig

    @classmethod
    def create(cls) -> "AppConfig":
        env = os.getenv("ENV", "base")
        path = Path(__file__).parent / "settings"
        config_factory = ConfigFactory.parse_file(path / f"{env}.conf")
        config_factory = config_factory.with_fallback(path / "base.conf")
        return cls(**dict(config_factory))


APP_CONFIG = AppConfig.create()
