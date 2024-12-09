from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from prometheus_client.exposition import make_asgi_app
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette_prometheus import PrometheusMiddleware

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

    @asynccontextmanager
    async def lifespan(self, server: FastAPI):
        # Startup
        await self._db.start()
        await self._kafka_producer.start()
        yield
        # Shutdown
        await self._db.shutdown()
        await self._kafka_producer.stop()

    def setup(self, server: FastAPI) -> None:
        @server.get("/favicon.ico")
        async def _favicon():
            return FileResponse("favicon.ico")

        if cors_origin_regex := self._config.cors_origin_regex:
            server.add_middleware(
                CORSMiddleware,
                allow_origin_regex=cors_origin_regex,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        if self._config.sentry_dsn and self._config.environment != "test":
            sentry_sdk.init(self._config.sentry_dsn)
            server.add_middleware(SentryAsgiMiddleware)
            custom_logger.add(self._sentry_handler, level="ERROR")

        server.add_middleware(PrometheusMiddleware, filter_unhandled_paths=True)
        server.mount("/metrics", make_asgi_app())

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
            lifespan=self.lifespan,
        )
        self.setup(server)
        return server
