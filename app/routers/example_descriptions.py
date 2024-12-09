from typing import Any

calculate_request_example = {
    "declared_value": 1000.0,
    "category_type": "Glass",
    "published_at": "2020-06-01",
}


add_tariff_request_example = {
    "2020-06-01": [
        {"category_type": "Glass", "rate": "0.04"},
        {"category_type": "Other", "rate": "0.01"},
    ],
    "2020-07-01": [
        {"category_type": "Glass", "rate": "0.035"},
        {"category_type": "Other", "rate": "0.015"},
    ],
}

update_tariff_description: dict[str, dict[str, Any]] = {
    "tariff_id": {
        "examples": [
            {
                "name": "example",
                "value": "da73f1ac-ae75-42e1-a9dd-321ede80e2e6",
                "description": "The uuid of the tariff to update",
            },
        ],
    },
    "updated_tariff": {
        "examples": [
            {
                "name": "example",
                "value": {
                    "category_type": "Glass",
                    "rate": 0.77,
                },
                "description": "Updated tariff details",
            },
        ],
    },
}

delete_tariff_description: dict[str, Any] = {
    "examples": [
        {
            "name": "example",
            "value": "da73f1ac-ae75-42e1-a9dd-321ede80e2e6",
            "description": "The uuid of the tariff to delete",
        },
    ],
}
