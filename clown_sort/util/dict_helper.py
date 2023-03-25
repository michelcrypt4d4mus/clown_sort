from typing import Any


def get_dict_key_by_value(_dict: dict, value: Any) -> Any:
    """Inverse of the usual dict operation."""
    return list(_dict.keys())[list(_dict.values()).index(value)]
