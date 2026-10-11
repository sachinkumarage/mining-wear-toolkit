"""minewear: wear-life estimation and wear-material selection for mining equipment."""

from minewear.materials import (
    COEFFICIENT_TYPES,
    NUMERIC_PROPERTIES,
    SOURCE_QUALITIES,
    WEAR_MODES,
    Material,
    WearCoefficient,
    filter_by_category,
    load_materials,
    load_wear_coefficients,
    rank_by,
)

__version__ = "0.1.1"

__all__ = [
    "COEFFICIENT_TYPES",
    "NUMERIC_PROPERTIES",
    "SOURCE_QUALITIES",
    "WEAR_MODES",
    "Material",
    "WearCoefficient",
    "filter_by_category",
    "load_materials",
    "load_wear_coefficients",
    "rank_by",
]
