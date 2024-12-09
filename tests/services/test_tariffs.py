from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.models.tariff import TariffBase
from app.orm_models import Tariff


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tariff_data, expected_response_length, expected_exception",
    [
        (
            {
                date(2023, 10, 1): [
                    TariffBase(category_type="type1", rate=0.5),
                    TariffBase(category_type="type2", rate=0.75),
                ],
            },
            1,
            None,
        ),
        (
            {
                date(2023, 10, 1): [
                    TariffBase(category_type="type1", rate=0.5),
                    TariffBase(category_type="type2", rate=0.0),
                ],
            },
            None,
            ValueError("Invalid data provided for tariff creation."),
        ),
        (
            {
                date(2023, 10, 1): [
                    TariffBase(category_type="type1", rate=0.5),
                ],
            },
            None,
            SQLAlchemyError("Database error occurred"),
        ),
    ],
)
async def test_create_tariff(
    tariff_service,
    tariff_data,
    expected_response_length,
    expected_exception,
):
    if expected_exception is None:
        tariff_models = [
            Tariff(
                id=uuid4(),
                category_type=tariff.category_type,
                rate=tariff.rate,
                date_accession_id=uuid4(),
            )
            for tariff in tariff_data[date(2023, 10, 1)]
        ]
        tariff_service._tariff_repo.add_tariffs_with_date_accession = AsyncMock(
            return_value=tariff_models,
        )
    else:
        tariff_service._tariff_repo.add_tariffs_with_date_accession.side_effect = (
            expected_exception
        )

    if expected_exception:
        with pytest.raises(HTTPException) as exc_info:
            await tariff_service.create_tariff(tariff_data)
        assert exc_info.value.status_code == (
            400 if isinstance(expected_exception, ValueError) else 500
        )
    else:
        response = await tariff_service.create_tariff(tariff_data)
        assert len(response) == expected_response_length
        assert len(response[0].tariffs) == 2
        assert response[0].tariffs[0].category_type == "type1"
        assert response[0].tariffs[0].rate == 0.5
