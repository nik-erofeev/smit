import uuid

from app import orm_models
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.orm_models import IdMixin
from app.utils.db import Base


class Rate(IdMixin, Base):
    __tablename__ = "rates"

    category_type: Mapped[str] = mapped_column(String(32))
    rate: Mapped[float] = mapped_column(Float)

    rate_date_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rate_dates.id", ondelete="CASCADE"),
        nullable=False,
    )

    rate_date: Mapped["orm_models.rate_date.RateDate"] = relationship(
        "RateDate",
        back_populates="rates",
    )
