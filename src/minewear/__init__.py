"""minewear: wear-life estimation and wear-material selection for mining equipment."""

from minewear.materials import (
    IMPACT_LEVELS,
    NUMERIC_PROPERTIES,
    Material,
    filter_by_category,
    load_materials,
    rank_by,
)

__version__ = "0.1.0"

__all__ = [
    "IMPACT_LEVELS",
    "NUMERIC_PROPERTIES",
    "Material",
    "filter_by_category",
    "load_materials",
    "rank_by",
]
