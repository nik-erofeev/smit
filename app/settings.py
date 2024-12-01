import os
from pathlib import Path

from pydantic import BaseModel
from pyhocon import ConfigFactory  # type: ignore

from app.utils.db import DbConfig


class AppConfig(BaseModel):
    bd: DbConfig

    @classmethod
    def create(cls) -> "AppConfig":
        env = os.getenv("ENV", "base")
        path = Path(__file__).parent / "settings"
        config_factory = ConfigFactory.parse_file(path / f"{env}.conf")
        config_factory = config_factory.with_fallback(path / "base.conf")
        return cls(**dict(config_factory))


APP_CONFIG = AppConfig.create()
