from datetime import date

from app.models.tariff import TariffCreate


def test_tariff_model(json_data_tariff):
    tariff = TariffCreate(**json_data_tariff)
    assert tariff.published_at == date(2020, 6, 1)
    assert len(tariff.rates) == 2

    assert tariff.rates[0].category_type == "Glass"
    assert tariff.rates[0].rate == 0.04
    assert tariff.rates[1].category_type == "Other"
    assert tariff.rates[1].rate == 0.01
