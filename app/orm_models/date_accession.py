from datetime import date

from sqlalchemy import Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import orm_models
from app.orm_models import IdMixin
from app.utils.db import Base


class DateAccession(IdMixin, Base):
    __tablename__ = "date_accessions"  # type: ignore

    published_at: Mapped[date] = mapped_column(
        Date,
        server_default=func.current_date(),
    )

    tariffs: Mapped[list["orm_models.tariff.Tariff"]] = relationship(
        "Tariff",
        back_populates="date_accession",
        cascade="all, delete-orphan",
    )
