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

    async def add_tariffs_with_date_accession(
        self,
        date_accession: date,
        tariffs: list[TariffBase],
    ) -> list[Tariff]:
        async with self._db.get_session() as session:
            date_accession_model = DateAccession(published_at=date_accession)
            session.add(date_accession_model)
            await session.flush()

            tariff_models = []
            for tariff in tariffs:
                rate_model = Tariff(
                    category_type=tariff.category_type,
                    rate=tariff.rate,
                    date_accession_id=date_accession_model.id,
                )
                session.add(rate_model)
                tariff_models.append(rate_model)

            await session.commit()
            return tariff_models

    async def get_tariff(
        self,
        effective_date: date,
        category_type: str,
    ) -> Tariff | None:
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

    async def get_tariff_by_id(self, tariff_id: UUID) -> Tariff | None:
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
