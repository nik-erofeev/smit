from datetime import date
from uuid import UUID

from app.models.rate import RateBase
from app.orm_models import Rate, RateDate
from app.utils.db import Db


class RateRepo:
    def __init__(self, db: Db):
        self._db = db

    async def add_rate_date(self, effective_date: date) -> RateDate:
        async with self._db.get_session() as session:
            rate_date = RateDate(effective_date=effective_date)
            session.add(rate_date)
            await session.flush()
            return rate_date

    async def add_rate(self, rate: RateBase, rate_date_id: UUID) -> Rate:
        async with self._db.get_session() as session:
            rate_model = Rate(
                category_type=rate.category_type,
                rate=rate.rate,
                rate_date_id=rate_date_id,
            )
            session.add(rate_model)
            await session.flush()
            await session.commit()
            return rate_model
