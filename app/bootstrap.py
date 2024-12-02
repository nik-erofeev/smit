from punq import Container, Scope

from app.kafka.producer import KafkaProducer
from app.repositories.tariff_repository import TariffRepo
from app.routers.default_router import DefaultRouter
from app.routers.tariff_router import TariffRouter
from app.services.tariff_service import TariffService
from app.settings import AppConfig
from app.utils.db import Db, DbConfig


def bootstrap(app_config: AppConfig) -> Container:
    container = Container()
    container.register(AppConfig, instance=app_config)
    container.register(DbConfig, instance=app_config.bd, scope=Scope.singleton)
    container.register(Db, Db, scope=Scope.singleton)

    kafka_producer = KafkaProducer(
        bootstrap_servers=app_config.kafka.bootstrap_servers,
        default_topic=app_config.kafka.topik,
    )
    container.register(KafkaProducer, instance=kafka_producer, scope=Scope.singleton)

    container.register(TariffRepo)
    container.register(TariffService)
    container.register(TariffRouter)

    container.register(DefaultRouter, DefaultRouter)

    return container
