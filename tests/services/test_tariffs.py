from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.tariff import InsuranceCostRequest, TariffBase, TariffResponse
from app.orm_models import DateAccession, Tariff


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tariff_data, expected_response_length",
    [
        (
            {
                date(2023, 10, 1): [
                    TariffBase(category_type="type1", rate=0.5),
                    TariffBase(category_type="type2", rate=0.75),
                ],
            },
            1,
        ),
        (
            {
                date(2023, 10, 1): [
                    TariffBase(category_type="type1", rate=0.5),
                    TariffBase(category_type="type2", rate=0.0),
                ],
            },
            1,
        ),
        (
            {
                date(2023, 10, 1): [
                    TariffBase(category_type="type1", rate=0.5),
                ],
            },
            1,
        ),
    ],
)
async def test_create_tariff(
    tariff_service_mock,
    tariff_data,
    expected_response_length,
):
    # Создаем моки для тарифов
    tariff_models = [
        Tariff(
            id=uuid4(),
            category_type=tariff.category_type,
            rate=tariff.rate,
            date_accession_id=uuid4(),
        )
        for tariff in tariff_data[date(2023, 10, 1)]
    ]

    # Настраиваем мок для успешного добавления тарифов
    tariff_service_mock._tariff_repo.add_tariffs_with_date_accession.return_value = (
        tariff_models
    )

    # Выполняем вызов метода create_tariff
    response = await tariff_service_mock.create_tariff(tariff_data)

    # Проверяем, что ответ содержит ожидаемое количество тарифов
    assert len(response) == expected_response_length
    assert len(response[0].tariffs) == len(tariff_data[date(2023, 10, 1)])
    assert response[0].tariffs[0].category_type == "type1"
    assert response[0].tariffs[0].rate == 0.5


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_data, expected_cost, expected_exception",
    [
        (
            InsuranceCostRequest(
                declared_value=1000,
                category_type="type1",
                published_at=date(2023, 10, 1),
            ),
            500.0,
            None,
        ),
        (
            InsuranceCostRequest(
                declared_value=1000,
                category_type="type2",
                published_at=date(2023, 10, 1),
            ),
            750.0,
            None,
        ),
        (
            InsuranceCostRequest(
                declared_value=1000,
                category_type="type3",
                published_at=date(2023, 10, 1),
            ),
            None,
            HTTPException(
                status_code=404,
                detail="Rate not found for the given date and category type",
            ),
        ),
    ],
)
async def test_calculate_insurance_cost(
    tariff_service_mock,
    request_data,
    expected_cost,
    expected_exception,
):
    if expected_exception is None:
        tariff_service_mock._tariff_repo.get_tariff.return_value = Tariff(
            rate=0.5 if request_data.category_type == "type1" else 0.75,
        )

    else:
        tariff_service_mock._tariff_repo.get_tariff.side_effect = expected_exception

    if expected_exception:
        with pytest.raises(HTTPException) as exc_info:
            await tariff_service_mock.calculate_insurance_cost(request_data)
        assert exc_info.value.status_code == expected_exception.status_code
    else:
        response = await tariff_service_mock.calculate_insurance_cost(request_data)
        assert response.insurance_cost == expected_cost


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tariff_id, existing_tariff, expected_exception",
    [
        (uuid4(), Tariff(id=uuid4(), category_type="type1", rate=0.5), None),
        (uuid4(), None, HTTPException(status_code=404, detail="Tariff not found")),
    ],
)
async def test_get_tariff_by_id(
    tariff_service_mock,
    tariff_id,
    existing_tariff,
    expected_exception,
):
    tariff_service_mock._tariff_repo.get_tariff_by_id.return_value = existing_tariff

    if expected_exception:
        with pytest.raises(HTTPException) as exc_info:
            await tariff_service_mock.get_tariff_by_id(tariff_id)
        assert exc_info.value.status_code == expected_exception.status_code
        assert exc_info.value.detail == expected_exception.detail
    else:
        response = await tariff_service_mock.get_tariff_by_id(tariff_id)
        assert response == existing_tariff


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tariff_id, new_tariff, existing_tariff, expected_response, expected_exception",
    [
        (
            uuid4(),
            TariffBase(category_type="type1", rate=0.6),
            Tariff(
                id=uuid4(),
                category_type="type1",
                rate=0.5,
                date_accession=DateAccession(published_at=date(2023, 10, 1)),
            ),
            None,
            None,
        ),
        (
            uuid4(),
            TariffBase(category_type="type1", rate=0.6),
            None,
            None,
            HTTPException(status_code=404, detail="Tariff not found"),
        ),
    ],
)
async def test_update_tariff(
    tariff_service_mock,
    tariff_id,
    new_tariff,
    existing_tariff,
    expected_response,
    expected_exception,
):
    tariff_service_mock.get_tariff_by_id = AsyncMock(return_value=existing_tariff)

    if expected_exception is None:
        updated_tariff = Tariff(
            id=tariff_id,
            category_type=new_tariff.category_type,
            rate=new_tariff.rate,
        )
        tariff_service_mock._tariff_repo.update_tariff.return_value = updated_tariff

        expected_response = TariffResponse(
            id=tariff_id,
            published_at=date(2023, 10, 1),
            tariffs=[TariffBase(category_type="type1", rate=0.6)],
        )
    else:
        tariff_service_mock._tariff_repo.update_tariff.side_effect = expected_exception

    if expected_exception:
        with pytest.raises(HTTPException) as exc_info:
            await tariff_service_mock.update_tariff(tariff_id, new_tariff)
        assert exc_info.value.status_code == expected_exception.status_code
    else:
        response = await tariff_service_mock.update_tariff(tariff_id, new_tariff)
        assert response == expected_response


GLOBAL_TARIFF_ID = uuid4()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "existing_tariff, expected_response, expected_exception",
    [
        (
            Tariff(id=GLOBAL_TARIFF_ID, category_type="type1", rate=0.5),
            {"message": f"Tariff with ID {GLOBAL_TARIFF_ID} has been deleted."},
            None,
        ),
        (
            None,
            None,
            HTTPException(status_code=404, detail="Tariff not found"),
        ),
    ],
)
async def test_delete_tariff(
    tariff_service_mock,
    existing_tariff,
    expected_response,
    expected_exception,
):
    tariff_service_mock.get_tariff_by_id = AsyncMock(return_value=existing_tariff)

    if expected_exception is None:
        tariff_service_mock._tariff_repo.delete_tariff = AsyncMock()
    else:
        tariff_service_mock._tariff_repo.delete_tariff.side_effect = expected_exception

    if expected_exception:
        with pytest.raises(HTTPException) as exc_info:
            await tariff_service_mock.delete_tariff(GLOBAL_TARIFF_ID)
        assert exc_info.value.status_code == expected_exception.status_code
    else:
        response = await tariff_service_mock.delete_tariff(GLOBAL_TARIFF_ID)
        assert response == expected_response
