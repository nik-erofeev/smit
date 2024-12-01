from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.tariff import TariffBase
from app.orm_models import DateAccession, Tariff
from app.utils.db import Db


class TariffRepo:
    def __init__(self, db: Db):
        self._db = db

    async def add_date_accession(self, date_accession: date) -> DateAccession:
        async with self._db.get_session() as session:
            date_accession = DateAccession(published_at=date_accession)
            session.add(date_accession)
            await session.flush()
            return date_accession

    async def add_tariff(self, tariff: TariffBase, tariff_date_id: UUID) -> Tariff:
        async with self._db.get_session() as session:
            rate_model = Tariff(
                category_type=tariff.category_type,
                rate=tariff.rate,
                date_accession_id=tariff_date_id,
            )
            session.add(rate_model)
            await session.flush()
            await session.commit()
            return rate_model

    async def get_tariff(self, effective_date: date, category_type: str):
        async with self._db.get_session() as session:
            result = await session.execute(
                select(Tariff)
                .options(
                    joinedload(Tariff.date_accession),
                )
                .join(DateAccession)
                .where(DateAccession.published_at == effective_date)
                .where(Tariff.category_type == category_type),
            )
            return result.scalars().first()

    async def get_tariff_by_id(self, tariff_id: UUID):
        async with self._db.get_session() as session:
            result = await session.execute(
                select(Tariff)
                .options(joinedload(Tariff.date_accession))
                .where(Tariff.id == tariff_id),
            )
            return result.scalars().first()

    async def update_tariff(self, tariff: Tariff) -> Tariff:
        async with self._db.get_session() as session:
            session.add(tariff)
            await session.commit()
            return tariff

    async def delete_tariff(self, tariff: Tariff) -> None:
        async with self._db.get_session() as session:
            await session.delete(tariff)
            await session.commit()
