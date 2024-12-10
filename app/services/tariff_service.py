import json
from datetime import date, datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException, UploadFile
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from app.kafka.producer import KafkaProducer
from app.models.action_type import ActionType
from app.models.tariff import (
    InsuranceCostRequest,
    InsuranceCostResponse,
    TariffBase,
    TariffResponse,
)
from app.orm_models import Tariff
from app.repositories.tariff_repository import TariffRepo


class TariffFileProcessor:
    @staticmethod
    def process_file(contents: bytes) -> dict[date, list[TariffBase]]:
        try:
            data = json.loads(contents)
            tariffs = {}
            for date_str, tariff_list in data.items():
                published_at = date.fromisoformat(date_str)
                tariff_objects = [TariffBase(**tariff) for tariff in tariff_list]
                tariffs[published_at] = tariff_objects
                logger.info(
                    f"Processed rates for date {published_at}: {tariff_objects}",
                )
            return tariffs
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
    def __init__(self, tariff_repo: TariffRepo, kafka_producer: KafkaProducer):
        self._tariff_repo = tariff_repo
        self._kafka_producer = kafka_producer

    @staticmethod
    def _create_message(
        action: ActionType,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "user_id": user_id,
            "action": action.value,
            "timestamp": str(datetime.now()),
        }

    async def create_tariff(
        self,
        tariff_data: dict[date, list[TariffBase]],
    ) -> list[TariffResponse]:
        response_tariffs = []
        for published_at, tariff_list in tariff_data.items():
            try:
                tariff_models = await self._tariff_repo.add_tariffs_with_date_accession(
                    published_at,
                    tariff_list,
                )
                example_user_id = tariff_models[0].date_accession_id

                response_tariffs.append(
                    TariffResponse(
                        id=example_user_id,
                        published_at=published_at,
                        tariffs=tariff_list,
                    ),
                )
                logger.info(
                    f"Successfully created tariffs for published_at {published_at}.",
                )

                message = self._create_message(
                    ActionType.CREATE_TARIFF,
                    str(example_user_id),
                )
                await self._kafka_producer.send_message(message)

            except SQLAlchemyError as e:
                logger.exception(f"Database error occurred while adding tariff: {e}")
                raise HTTPException(status_code=500, detail="Database error occurred")
            except ValueError as value_error:
                logger.exception("Invalid data provided for tariff creation.")
                raise HTTPException(status_code=400, detail=str(value_error))

        logger.info(f"Created {len(response_tariffs)} tariffs successfully.")
        return response_tariffs

    async def upload_tariff(self, file: UploadFile) -> list[TariffResponse]:
        contents = await file.read()
        tariffs_data = TariffFileProcessor.process_file(contents)
        logger.info(f"Tariff file {file.filename} uploaded and processed.")
        return await self.create_tariff(tariffs_data)

    async def calculate_insurance_cost(
        self,
        request: InsuranceCostRequest,
    ) -> InsuranceCostResponse:
        result = await self._tariff_repo.get_tariff(
            request.published_at,
            request.category_type,
        )

        if result is None:
            logger.warning(
                f"Rate not found for the given date {request.published_at} and category type: {request.category_type}.",  # noqa: E501
            )
            raise HTTPException(
                status_code=404,
                detail="Rate not found for the given date and category type",
            )

        insurance_cost = request.declared_value * result.rate
        logger.info(
            f"Insurance cost calculated: {insurance_cost} for declared value: {request.declared_value} and rate: {result.rate}.",  # noqa: E501
        )

        message = self._create_message(ActionType.CALCULATE_INSURANCE_COST)
        await self._kafka_producer.send_message(message)

        return InsuranceCostResponse(
            declared_value=request.declared_value,
            category_type=request.category_type,
            published_at=request.published_at,
            rate=result.rate,
            insurance_cost=insurance_cost,
        )

    async def get_tariff_by_id(self, tariff_id: UUID) -> Tariff | None:
        tariff = await self._tariff_repo.get_tariff_by_id(tariff_id)
        if not tariff:
            raise HTTPException(status_code=404, detail="Tariff not found")
        return tariff

    async def update_tariff(
        self,
        tariff_id: UUID,
        new_tariff: TariffBase,
    ) -> TariffResponse:
        old_tariff = await self.get_tariff_by_id(tariff_id)

        if not old_tariff:
            logger.warning(f"Tariff with ID {tariff_id} not found.")
            raise HTTPException(status_code=404, detail="Tariff not found")

        old_tariff.category_type = new_tariff.category_type
        old_tariff.rate = new_tariff.rate
        updated_tariff = await self._tariff_repo.update_tariff(old_tariff)
        logger.info(
            f"Tariff with ID {tariff_id} updated successfully: {updated_tariff}.",
        )

        message = self._create_message(ActionType.UPDATE_TARIFF)

        await self._kafka_producer.send_message(message)

        return TariffResponse(
            id=updated_tariff.id,
            published_at=old_tariff.date_accession.published_at,
            tariffs=[
                TariffBase(
                    category_type=updated_tariff.category_type,
                    rate=updated_tariff.rate,
                ),
            ],
        )

    async def delete_tariff(self, tariff_id: UUID) -> dict[str, str]:
        tariff = await self.get_tariff_by_id(tariff_id)
        if not tariff:
            logger.warning(f"Tariff with ID {tariff_id} not found.")
            raise HTTPException(status_code=404, detail="Tariff not found")

        await self._tariff_repo.delete_tariff(tariff)

        message = self._create_message(ActionType.DELETE_TARIFF)
        await self._kafka_producer.send_message(message)

        logger.info(f"Tariff with ID {tariff_id} has been deleted successfully.")
        return {"message": f"Tariff with ID {tariff_id} has been deleted."}
