import logging
from datetime import date

from fastapi import APIRouter, Body, UploadFile, File
from fastapi.responses import ORJSONResponse

from app.models.rate import RateResponse, RateBase
from app.services.rate_service import RateService

logger = logging.getLogger(__name__)


class RateRouter:
    def __init__(self, rate_service: RateService):
        self._rate_service = rate_service

    @property
    def api_route(self) -> APIRouter:
        router = APIRouter()
        self._register(router)
        return router

    def _register(self, router: APIRouter):
        @router.post(
            "/",
            response_model=list[RateResponse],
            response_class=ORJSONResponse,
            status_code=201,
        )
        async def add_rate(
            rates: dict[date, list[RateBase]] = Body(
                ...,
                example={
                    "2020-06-01": [
                        {"category_type": "Glass", "rate": "0.04"},
                        {"category_type": "Other", "rate": "0.01"},
                    ],
                    "2020-07-01": [
                        {"category_type": "Glass", "rate": "0.035"},
                        {"category_type": "Other", "rate": "0.015"},
                    ],
                },
            )
        ):
            return await self._rate_service.create_rates(rates)

        @router.post(
            "/upload/",
            response_model=list[RateResponse],
            response_class=ORJSONResponse,
            status_code=201,
        )
        async def upload_rates(file: UploadFile = File(...)):
            return await self._rate_service.upload_rates(file)
