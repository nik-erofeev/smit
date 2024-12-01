from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class TariffBase(BaseModel):
    category_type: str = Field(max_length=20, description="Категория тарифа")
    rate: float = Field(ge=0, le=1, description="Рейтинг тарифа")


class UpdateTariff(TariffBase):
    pass


class TariffCreate(BaseModel):
    published_at: date = Field(description="Дата публикации тарифа")
    rates: list[TariffBase]


class TariffResponse(BaseModel):
    id: UUID
    published_at: date
    tariffs: list[TariffBase]


class InsuranceCostBase(BaseModel):
    declared_value: float = Field(ge=0, description="Объявленная стоимость")
    category_type: str = Field(max_length=20, description="Категория тарифа")
    published_at: date = Field(description="Дата публикации тарифа")


class InsuranceCostRequest(InsuranceCostBase):
    pass


class InsuranceCostResponse(InsuranceCostBase):
    rate: float = Field(ge=0, le=1, description="Рейтинг тарифа")
    insurance_cost: float = Field(ge=0, description="Стоимость страхования")
