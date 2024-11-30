from datetime import date

from app import orm_models
from sqlalchemy import Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.orm_models import IdMixin
from app.utils.db import Base


class RateDate(IdMixin, Base):
    __tablename__ = "rate_dates"

    effective_date: Mapped[date] = mapped_column(
        Date, server_default=func.current_date()
    )

    rates: Mapped[list["orm_models.rate.Rate"]] = relationship(
        "Rate", back_populates="rate_date", cascade="all, delete-orphan"
    )
