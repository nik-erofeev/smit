from datetime import date
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class RateBase(BaseModel):
    category_type: str
    rate: float


class RateCreate(BaseModel):
    effective_date: date
    rates: List[RateBase]


class RateResponse(BaseModel):
    id: UUID
    effective_date: date
    rates: List[RateBase]
