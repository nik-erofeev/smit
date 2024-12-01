from enum import Enum


class ActionType(str, Enum):
    CREATE_TARIFF = "create_tariff"
    CALCULATE_INSURANCE_COST = "calculate_insurance_cost"
    UPDATE_TARIFF = "update_tariff"
    DELETE_TARIFF = "delete_tariff"
