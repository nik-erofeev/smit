from datetime import date
from uuid import UUID

from fastapi import APIRouter, Body, File, Path, UploadFile
from fastapi.responses import ORJSONResponse

from app.models.tariff import (
    InsuranceCostRequest,
    InsuranceCostResponse,
    TariffBase,
    TariffResponse,
)
from app.routers.example_descriptions import (
    add_tariff_request_example,
    calculate_request_example,
    delete_tariff_description,
    update_tariff_description,
)
from app.services.tariff_service import TariffService


class TariffRouter:
    def __init__(self, tariff_service: TariffService):
        self._tariff_service = tariff_service

    @property
    def api_route(self) -> APIRouter:
        router = APIRouter()
        self._register(router)
        return router

    def _register(self, router: APIRouter) -> None:
        @router.post(
            "/",
            response_model=list[TariffResponse],
            response_class=ORJSONResponse,
            status_code=201,
        )
        async def add_tariff(
            tariff: dict[date, list[TariffBase]] = Body(
                ...,
                example=add_tariff_request_example,
            ),
        ) -> list[TariffResponse]:
            return await self._tariff_service.create_tariff(tariff)

        @router.post(
            "/upload/",
            response_model=list[TariffResponse],
            response_class=ORJSONResponse,
            status_code=201,
        )
        async def upload_tariffs(file: UploadFile = File(...)) -> list[TariffResponse]:
            return await self._tariff_service.upload_tariff(file)

        @router.post(
            "/calculate/",
            response_model=InsuranceCostResponse,
            response_class=ORJSONResponse,
            status_code=200,
        )
        async def calculate_cost(
            request: InsuranceCostRequest = Body(
                ...,
                example=calculate_request_example,
            ),
        ) -> InsuranceCostResponse:
            return await self._tariff_service.calculate_insurance_cost(request)

        @router.put(
            "/{tariff_id}/",
            response_model=TariffResponse,
            response_class=ORJSONResponse,
            status_code=200,
        )
        async def update_tariff(
            tariff_id: UUID = Path(
                ...,
                **update_tariff_description["tariff_id"],
            ),
            updated_tariff: TariffBase = Body(
                ...,
                **update_tariff_description["updated_tariff"],
            ),
        ) -> TariffResponse:
            return await self._tariff_service.update_tariff(tariff_id, updated_tariff)

        @router.delete(
            "/{tariff_id}/",
            response_class=ORJSONResponse,
            status_code=204,
        )
        async def delete_tariff(
            tariff_id: UUID = Path(
                ...,
                **delete_tariff_description,
            ),
        ) -> ORJSONResponse:
            result = await self._tariff_service.delete_tariff(tariff_id)
            return ORJSONResponse(content=result, status_code=200)
