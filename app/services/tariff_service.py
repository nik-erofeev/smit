import json
from loguru import logger
from datetime import date
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError

from app.models.tariff import (
    TariffResponse,
    TariffBase,
    InsuranceCostRequest,
    InsuranceCostResponse,
)
from app.repositories.tariff_repository import TariffRepo


class RateFileProcessor:
    @staticmethod
    def process_file(contents: bytes) -> dict[date, list[TariffBase]]:
        try:
            rates_data = json.loads(contents)
            date_rates = {}
            for date_str, rate_list in rates_data.items():
                effective_date = date.fromisoformat(date_str)
                rate_objects = [TariffBase(**rate) for rate in rate_list]
                date_rates[effective_date] = rate_objects
                logger.debug(
                    f"Processed rates for date {effective_date}: {rate_objects}",
                )
            return date_rates
        except json.JSONDecodeError:
            logger.exception("Invalid JSON format.")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as e:
            logger.exception(f"An error occurred while processing the file: {e}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while processing the file",
            )


class TariffService:
    def __init__(self, tariff_repo: TariffRepo):
        self._tariff_repo = tariff_repo

    async def create_tariff(
        self,
        tariff_data: dict[date, list[TariffBase]],
    ) -> list[TariffResponse]:
        response_tariffs = []
        for published_at, tariff_list in tariff_data.items():
            try:
                date_accession = await self._tariff_repo.add_date_accession(
                    published_at,
                )
                await self._add_tariff(tariff_list, date_accession.id)
                response_tariffs.append(
                    TariffResponse(
                        id=date_accession.id,
                        published_at=published_at,
                        tariffs=tariff_list,
                    ),
                )
                logger.info(
                    f"Successfully created tariff with id {date_accession.id} for published_at {published_at}.",
                )
            except SQLAlchemyError as e:
                logger.exception(f"Database error occurred while adding tariff: {e}")
                raise HTTPException(status_code=500, detail="Database error occurred")
            except ValueError as value_error:
                logger.exception("Invalid data provided for tariff creation.")
                raise HTTPException(status_code=400, detail=str(value_error))

        logger.info(f"Created {len(response_tariffs)} tariffs successfully.")
        return response_tariffs

    async def _add_tariff(self, tariff_list: list[TariffBase], tariff_date_id: str):
        for tariff in tariff_list:
            await self._tariff_repo.add_tariff(tariff, tariff_date_id)

    async def upload_tariff(self, file: UploadFile) -> list[TariffResponse]:
        contents = await file.read()
        date_tariff = RateFileProcessor.process_file(contents)
        logger.info(f"Tariff file {file.filename} uploaded and processed.")
        return await self.create_tariff(date_tariff)

    async def calculate_insurance_cost(self, request: InsuranceCostRequest) -> float:
        result = await self._tariff_repo.get_tariff(
            request.published_at,
            request.category_type,
        )

        if result is None:
            logger.warning(
                f"Rate not found for the given date {request.published_at} and category type: {request.category_type}.",
            )
            raise HTTPException(
                status_code=404,
                detail="Rate not found for the given date and category type",
            )

        insurance_cost = request.declared_value * result.rate
        logger.info(
            f"Insurance cost calculated: {insurance_cost} for declared value: {request.declared_value} and rate: {result.rate}.",
        )
        return InsuranceCostResponse(
            declared_value=request.declared_value,
            category_type=request.category_type,
            published_at=request.published_at,
            rate=result.rate,
            insurance_cost=insurance_cost,
        )

    async def get_tariff_by_id(self, tariff_id: UUID):
        return await self._tariff_repo.get_tariff_by_id(tariff_id)

    async def update_tariff(
        self,
        tariff_id: UUID,
        updated_tariff: TariffBase,
    ) -> TariffResponse:
        tariff = await self.get_tariff_by_id(tariff_id)

        if not tariff:
            logger.warning(f"Tariff with ID {tariff_id} not found.")
            raise HTTPException(status_code=404, detail="Tariff not found")

        tariff.category_type = updated_tariff.category_type
        tariff.rate = updated_tariff.rate
        updated_tariff = await self._tariff_repo.update_tariff(tariff)
        logger.info(
            f"Tariff with ID {tariff_id} updated successfully: {updated_tariff}.",
        )

        return TariffResponse(
            id=updated_tariff.id,
            published_at=tariff.date_accession.published_at,
            tariffs=[
                TariffBase(
                    category_type=updated_tariff.category_type,
                    rate=updated_tariff.rate,
                ),
            ],
        )

    async def delete_tariff(self, tariff_id: UUID) -> None:
        tariff = await self.get_tariff_by_id(tariff_id)
        if not tariff:
            logger.warning(f"Tariff with ID {tariff_id} not found.")
            raise HTTPException(status_code=404, detail="Tariff not found")

        await self._tariff_repo.delete_tariff(tariff)
        logger.info(f"Tariff with ID {tariff_id} has been deleted successfully.")
        return {"message": f"Tariff with ID {tariff_id} has been deleted."}
