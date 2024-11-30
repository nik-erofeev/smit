import logging

from fastapi import FastAPI

from app.routers.rate_router import RateRouter
from app.settings import AppConfig
from app.utils.db import Db


logger = logging.getLogger(__name__)


class Application:
    def __init__(
        self,
        config: AppConfig,
        db: Db,
        rate: RateRouter,
    ):
        self._config = config
        self._db = db
        self._rate = rate

    def setup(self, server: FastAPI) -> None:
        @server.on_event("startup")
        async def on_startup() -> None:
            await self._db.start()

        @server.on_event("shutdown")
        async def on_shutdown() -> None:
            await self._db.shutdown()

        server.include_router(self._rate.api_route, prefix="/rates", tags=["Рейтинг"])

    @property
    def app(self) -> FastAPI:
        server = FastAPI(
            title="Test project",
            description="тестовый проект",
            version="0.1.0",
            contact={
                "name": "Nik",
                "email": "erofeev.nik.it@yandex.ru",
            },
            license_info={"name": "TEST_license"},
        )
        self.setup(server)
        return server
