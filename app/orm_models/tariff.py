import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import orm_models
from app.orm_models import IdMixin
from app.utils.db import Base


class Tariff(IdMixin, Base):
    __tablename__ = "tariffs"

    category_type: Mapped[str] = mapped_column(String(32))
    rate: Mapped[float] = mapped_column(Float)

    date_accession_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("date_accessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    date_accession: Mapped["orm_models.date_accession.DateAccession"] = relationship(
        "DateAccession",
        back_populates="tariffs",
    )
