from unittest.mock import AsyncMock

import pytest
from asyncpg.pool import Pool

from app.kafka.producer import KafkaProducer
from app.repositories.tariff_repository import TariffRepo
from app.services.tariff_service import TariffService


@pytest.fixture
def db_mock():
    return AsyncMock(autospec=Pool)


@pytest.fixture
def tariff_repository_mock():
    return AsyncMock(autospec=TariffRepo)


@pytest.fixture
def kafka_producer_mock():
    return AsyncMock(autospec=KafkaProducer)


@pytest.fixture
def tariff_service(kafka_producer_mock, tariff_repository_mock):
    return TariffService(tariff_repository_mock, kafka_producer_mock)
