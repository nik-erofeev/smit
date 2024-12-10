from loguru import logger
from punq import Container, Scope

from app.kafka.producer import KafkaProducer
from app.repositories.tariff_repository import TariffRepo
from app.routers.default_router import DefaultRouter
from app.routers.tariff_router import TariffRouter
from app.services.tariff_service import TariffService
from app.settings import AppConfig
from app.utils.db import Db


def bootstrap(app_config: AppConfig) -> Container:
    container = Container()

    try:
        container.register(AppConfig, instance=app_config)

        smit_db = Db(app_config.db)
        container.register(Db, instance=smit_db, scope=Scope.singleton)

        kafka_producer = KafkaProducer(
            bootstrap_servers=app_config.kafka.bootstrap_servers,
            default_topic=app_config.kafka.topik,
        )
        container.register(
            KafkaProducer,
            instance=kafka_producer,
            scope=Scope.singleton,
        )

        container.register(DefaultRouter, DefaultRouter)
        container.register(TariffRouter, TariffRouter)

        container.register(TariffService, TariffService)
        container.register(TariffRepo, TariffRepo)
    except Exception as e:
        logger.error(f"Error during bootstrap: {e}")
        raise
    return container
