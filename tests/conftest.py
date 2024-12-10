from unittest.mock import AsyncMock

import pytest
import sentry_sdk

from app.kafka.producer import KafkaProducer
from app.repositories.tariff_repository import TariffRepo
from app.services.tariff_service import TariffService
from app.utils.db import Db
from tests.utils import load_json


@pytest.fixture(autouse=True)
def disable_sentry(monkeypatch):
    # todo: Заменяем инициализации Sentry на пустую, что бы не отправлять в sentry тесты
    monkeypatch.setattr(sentry_sdk, "init", lambda *args, **kwargs: None)


@pytest.fixture
def db_mock():
    return AsyncMock(autospec=Db)


@pytest.fixture
def tariff_repository_mock():
    return AsyncMock(autospec=TariffRepo)


@pytest.fixture
def kafka_producer_mock():
    return AsyncMock(autospec=KafkaProducer)


@pytest.fixture
def tariff_service_mock(kafka_producer_mock, tariff_repository_mock):
    return TariffService(tariff_repository_mock, kafka_producer_mock)


@pytest.fixture
def json_data_tariff() -> dict:
    address = load_json("mocked_data/tariff.json")
    return address
