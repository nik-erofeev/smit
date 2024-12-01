from fastapi import FastAPI

from app.routers.tariff_router import TariffRouter
from app.settings import AppConfig
from app.utils.db import Db


class Application:
    def __init__(
        self,
        config: AppConfig,
        db: Db,
        rate: TariffRouter,
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

        server.include_router(
            self._rate.api_route,
            prefix="/v1/tariffs",
            tags=["Тарифы"],
        )

    @property
    def app(self) -> FastAPI:
        server = FastAPI(
            title="SmitAPP",
            description="SmitAPP API 🚀",
            version="0.1.0",
            contact={
                "name": "Nik",
                "email": "erofeev.nik.it@yandex.ru",
            },
            license_info={
                "name": "Apache 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
            },
            openapi_url="/api/v1/openapi.json",
        )
        self.setup(server)
        return server
