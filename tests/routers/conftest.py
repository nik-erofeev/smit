import pytest
from fastapi.testclient import TestClient
from punq import Container, Scope

from app.kafka.producer import KafkaProducer
from app.repositories.tariff_repository import TariffRepo
from app.routers.default_router import DefaultRouter
from app.routers.tariff_router import TariffRouter
from app.services.tariff_service import TariffService
from app.settings import AppConfig
from app.utils.db import Db


@pytest.fixture
def client(
    monkeypatch,  # для замены атрибутов
    db_mock,
    kafka_producer_mock,
):
    def bootstrap_mock(app_config: AppConfig):
        """Функция для создания контейнера зависимостей с моками"""

        container = Container()  # Создаем новый контейнер зависимостей
        container.register(AppConfig, instance=app_config)

        container.register(Db, instance=db_mock, scope=Scope.singleton)
        container.register(KafkaProducer, kafka_producer_mock, scope=Scope.singleton)

        container.register(TariffRepo)
        container.register(TariffService)
        container.register(TariffRouter)

        container.register(DefaultRouter, DefaultRouter)
        return container

    import main  # импорт main после определения bootstrap_mock
    from main import app  # импорт приложения FastAPI из main

    # todo: заменяем функцию bootstrap в main на нашу mock-версию
    monkeypatch.setattr(main, "bootstrap", bootstrap_mock)

    return TestClient(app)
