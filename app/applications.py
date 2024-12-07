import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app.kafka.producer import KafkaProducer
from app.routers.default_router import DefaultRouter
from app.routers.tariff_router import TariffRouter
from app.settings import AppConfig
from app.utils.db import Db
from app.utils.logger_config import logger as custom_logger


class Application:
    def __init__(
        self,
        config: AppConfig,
        db: Db,
        default: DefaultRouter,
        rate: TariffRouter,
        kafka_producer: KafkaProducer,
    ):
        self._config = config
        self._db = db
        self._default = default
        self._rate = rate
        self._kafka_producer = kafka_producer

    def setup(self, server: FastAPI) -> None:
        @server.on_event("startup")
        async def on_startup() -> None:
            await self._db.start()
            await self._kafka_producer.start()

        @server.on_event("shutdown")
        async def on_shutdown() -> None:
            await self._db.shutdown()
            await self._kafka_producer.stop()

        if sentry_dsn := self._config.sentry_dsn:
            sentry_sdk.init(sentry_dsn)
            server.add_middleware(SentryAsgiMiddleware)
            custom_logger.add(self._sentry_handler, level="ERROR")

        server.include_router(
            self._default.api_router,
            prefix="/default",
            tags=["Default"],
        )

        server.include_router(
            self._rate.api_route,
            prefix="/v1/tariffs",
            tags=["Тарифы"],
        )

    def _sentry_handler(self, message: str) -> None:
        """Отправляет сообщение в Sentry."""
        sentry_sdk.capture_message(message)

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
