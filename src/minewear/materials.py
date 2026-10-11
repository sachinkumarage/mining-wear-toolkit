"""Load, filter and rank the bundled wear-materials database.

All values in the database are indicative and intended for screening only.
Missing values are kept as ``None`` rather than filled with estimates.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, fields
from importlib import resources
from pathlib import Path
from typing import Iterable

IMPACT_LEVELS = ("low", "med", "high")

#: Numeric properties that :func:`rank_by` accepts.
NUMERIC_PROPERTIES = (
    "hardness_HB",
    "hardness_shore_A",
    "density_kg_m3",
    "relative_cost_index",
)


@dataclass(frozen=True)
class Material:
    """One row of the materials database."""

    name: str
    category: str
    hardness_HB: float | None
    hardness_shore_A: float | None
    density_kg_m3: float | None
    typical_applications: tuple[str, ...]
    impact_resistance: str | None
    relative_cost_index: float | None
    data_status: str
    source: str
    notes: str = ""


def _optional_float(value: str) -> float | None:
    value = value.strip()
    return float(value) if value else None


def _parse_row(row: dict[str, str]) -> Material:
    impact = row["impact_resistance"].strip().lower() or None
    if impact is not None and impact not in IMPACT_LEVELS:
        raise ValueError(
            f"{row['name']!r}: impact_resistance must be one of {IMPACT_LEVELS} "
            f"or blank, got {impact!r}"
        )
    applications = tuple(
        a.strip() for a in row["typical_applications"].split(";") if a.strip()
    )
    return Material(
        name=row["name"].strip(),
        category=row["category"].strip().lower(),
        hardness_HB=_optional_float(row["hardness_HB"]),
        hardness_shore_A=_optional_float(row["hardness_shore_A"]),
        density_kg_m3=_optional_float(row["density_kg_m3"]),
        typical_applications=applications,
        impact_resistance=impact,
        relative_cost_index=_optional_float(row["relative_cost_index"]),
        data_status=row["data_status"].strip(),
        source=row["source"].strip(),
        notes=row.get("notes", "").strip(),
    )


def load_materials(path: str | Path | None = None) -> list[Material]:
    """Load materials from ``path``, or from the bundled CSV if omitted."""
    if path is None:
        text = (
            resources.files("minewear")
            .joinpath("data/materials.csv")
            .read_text(encoding="utf-8")
        )
    else:
        text = Path(path).read_text(encoding="utf-8")

    reader = csv.DictReader(text.splitlines())
    expected = {f.name for f in fields(Material)}
    missing = expected - set(reader.fieldnames or ())
    if missing:
        raise ValueError(f"materials CSV is missing columns: {sorted(missing)}")
    return [_parse_row(row) for row in reader]


def filter_by_category(
    materials: Iterable[Material], category: str
) -> list[Material]:
    """Return materials whose category matches ``category`` (case-insensitive)."""
    wanted = category.strip().lower()
    return [m for m in materials if m.category == wanted]


def rank_by(
    materials: Iterable[Material], prop: str, descending: bool = True
) -> list[Material]:
    """Rank materials by one numeric property.

    Materials with no value for ``prop`` are excluded, never treated as zero.
    """
    if prop not in NUMERIC_PROPERTIES:
        raise ValueError(
            f"cannot rank by {prop!r}; choose one of {NUMERIC_PROPERTIES}"
        )
    with_value = [m for m in materials if getattr(m, prop) is not None]
    return sorted(with_value, key=lambda m: getattr(m, prop), reverse=descending)
