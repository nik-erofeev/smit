import json
import logging
from datetime import date
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.models.rate import RateResponse, RateBase
from app.repositories.rate_repository import RateRepo

logger = logging.getLogger(__name__)


class RateFileProcessor:
    """Класс для обработки файлов с данными."""

    @staticmethod
    def process_file(contents: bytes) -> dict[date, list[RateBase]]:
        try:
            rates_data = json.loads(contents)
            date_rates = {}
            for date_str, rate_list in rates_data.items():
                effective_date = date.fromisoformat(date_str)
                rate_objects = [RateBase(**rate) for rate in rate_list]
                date_rates[effective_date] = rate_objects
            return date_rates
        except json.JSONDecodeError:
            logger.exception("Invalid JSON format.")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as e:
            logger.exception(f"An error occurred while processing the file: {e}")
            raise HTTPException(
                status_code=500, detail="An error occurred while processing the file"
            )


class RateService:
    """Сервис для работы с ставками."""

    def __init__(self, rate_repo: RateRepo):
        self._rate_repo = rate_repo

    async def create_rates(
        self, rates_data: dict[date, list[RateBase]]
    ) -> list[RateResponse]:
        response_rates = []
        for effective_date, rate_list in rates_data.items():
            try:
                rate_date = await self._rate_repo.add_rate_date(effective_date)
                await self._add_rates(rate_list, rate_date.id)
                response_rates.append(
                    RateResponse(
                        id=rate_date.id, effective_date=effective_date, rates=rate_list
                    )
                )
            except SQLAlchemyError as e:
                logger.exception(f"Database error occurred while adding rates: {e}")
                raise HTTPException(status_code=500, detail="Database error occurred")
            except ValueError as value_error:
                logger.exception("Invalid data provided for rates creation.")
                raise HTTPException(status_code=400, detail=str(value_error))
        return response_rates

    async def _add_rates(self, rate_list: list[RateBase], rate_date_id: str):
        for rate in rate_list:
            await self._rate_repo.add_rate(rate, rate_date_id)

    async def upload_rates(self, file) -> list[RateResponse]:
        contents = await file.read()
        date_rates = RateFileProcessor.process_file(contents)
        return await self.create_rates(date_rates)
