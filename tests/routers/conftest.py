import pytest
from punq import Container, Scope
from starlette.testclient import TestClient

from app.kafka.producer import KafkaProducer
from app.repositories.tariff_repository import TariffRepo
from app.routers.default_router import DefaultRouter
from app.routers.tariff_router import TariffRouter
from app.services.tariff_service import TariffService
from app.settings import AppConfig
from app.utils.db import Db


@pytest.fixture
def client(
    monkeypatch,
    db_mock,
    kafka_producer_mock,
    tariff_repository_mock,
    tariff_service_mock,
):
    def bootstrap_mock(app_config: AppConfig):
        container = Container()

        container.register(AppConfig, instance=app_config)

        container.register(Db, instance=db_mock, scope=Scope.singleton)

        container.register(
            KafkaProducer,
            instance=kafka_producer_mock,
            scope=Scope.singleton,
        )

        container.register(DefaultRouter, DefaultRouter)
        container.register(TariffRouter, TariffRouter)

        container.register(TariffService, instance=tariff_service_mock)
        container.register(TariffRepo, instance=tariff_repository_mock)

        return container

    # todo:  Заменяем функцию bootstrap на нашу мок-версию
    monkeypatch.setattr("app.bootstrap.bootstrap", bootstrap_mock)

    # импорт main после определения bootstrap_mock
    from main import app

    return TestClient(app)
