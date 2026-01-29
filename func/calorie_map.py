import re
from typing import Tuple, Optional

# Calorie values based on dataset assumption
# Format: food_name : (calorie_value, unit_type)
# unit_type helps explanation in report (per 100g or per piece)
CALORIE_MAP = {
    "ayam goreng": (260, "100g"),
    "capcay": (67, "100g"),
    "nasi": (129, "100g"),
    "sayur bayam": (36, "100g"),
    "sayur kangkung": (98, "100g"),
    "sayur sop": (22, "100g"),
    "tahu": (80, "100g"),
    "telur dadar": (93, "100g"),
    "telur mata sapi": (110, "piece"),
    "telur rebus": (78, "piece"),
    "tempe": (225, "100g"),
    "tumis buncis": (65, "100g")
}


def normalize_label(label: str) -> str:
    """
    Normalize model label output to make matching robust.
    Steps:
    - convert to lowercase
    - remove numbers and special characters
    - remove extra spaces
    """
    label = label.lower()
    label = re.sub(r"[^a-z\s]", " ", label)  # keep only letters and spaces
    label = re.sub(r"\s+", " ", label).strip()
    return label


def match_food_label(label: str) -> Optional[str]:
    """
    Match normalized label to a known food name.
    Returns matched food key or None.
    """
    clean_label = normalize_label(label)

    for food_name in CALORIE_MAP.keys():
        if food_name in clean_label:
            return food_name

    return None


def get_calorie_info(label: str) -> Tuple[int, str]:
    """
    Returns (calorie_value, unit_type) for a detected food label.
    If label is unknown, returns (0, "unknown").
    """
    food_key = match_food_label(label)

    if food_key:
        return CALORIE_MAP[food_key]

    print(f"[WARNING] Unknown food label detected: {label}")
    return 0, "unknown"


def get_calorie(label: str) -> int:
    """
    Returns only calorie value (used in total calorie calculation).
    Safe fallback = 0 kcal.
    """
    calories, _ = get_calorie_info(label)
    return calories


