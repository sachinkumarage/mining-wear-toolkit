"""Load, filter and rank the bundled wear-materials and wear-coefficient data.

All values are indicative and intended for screening only. Missing values are
kept as ``None`` rather than filled with estimates. Units are SI.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable
from dataclasses import dataclass, fields
from importlib import resources
from pathlib import Path

SOURCE_QUALITIES = ("primary", "secondary", "unverified")

WEAR_MODES = ("two_body_abrasion", "three_body_abrasion", "slurry_erosion")

COEFFICIENT_TYPES = (
    "dimensionless_k",
    "specific_wear_rate_mm3_per_Nm",
    "astm_g65_volume_loss_mm3",
    "iso4649_volume_loss_mm3",
)

#: Numeric material properties that :func:`rank_by` accepts.
NUMERIC_PROPERTIES = (
    "hardness_HB_min",
    "hardness_HB_max",
    "hardness_shore_A_min",
    "hardness_shore_A_max",
    "density_kg_m3",
    "charpy_J",
    "fracture_toughness_MPa_m05",
)


@dataclass(frozen=True)
class Material:
    """One row of the materials database."""

    name: str
    category: str
    hardness_HB_min: float | None
    hardness_HB_max: float | None
    hardness_shore_A_min: float | None
    hardness_shore_A_max: float | None
    density_kg_m3: float | None
    charpy_J: float | None
    charpy_test_temp_C: float | None
    fracture_toughness_MPa_m05: float | None
    typical_applications: tuple[str, ...]
    source: str
    test_method: str
    source_quality: str
    data_status: str
    notes: str = ""


@dataclass(frozen=True)
class WearCoefficient:
    """One row of the wear-coefficient database.

    ``low``, ``typical`` and ``high`` are ``None`` where no published value exists.
    """

    material: str
    wear_mode: str
    coefficient_type: str
    low: float | None
    typical: float | None
    high: float | None
    test_method: str
    source: str
    source_quality: str | None


def _optional_float(value: str) -> float | None:
    value = value.strip()
    return float(value) if value else None


def _check_choice(row_name: str, column: str, value: str, choices: tuple[str, ...]) -> None:
    if value not in choices:
        raise ValueError(f"{row_name!r}: {column} must be one of {choices}, got {value!r}")


def _check_range(row_name: str, label: str, low: float | None, high: float | None) -> None:
    if low is not None and high is not None and low > high:
        raise ValueError(f"{row_name!r}: {label} min {low} exceeds max {high}")


def _read_rows(filename: str, path: str | Path | None, expected: set[str]) -> list[dict[str, str]]:
    if path is None:
        text = resources.files("minewear").joinpath("data", filename).read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding="utf-8")

    reader = csv.DictReader(text.splitlines())
    missing = expected - set(reader.fieldnames or ())
    if missing:
        raise ValueError(f"{filename} is missing columns: {sorted(missing)}")
    return list(reader)


def _parse_material(row: dict[str, str]) -> Material:
    name = row["name"].strip()
    quality = row["source_quality"].strip().lower()
    _check_choice(name, "source_quality", quality, SOURCE_QUALITIES)

    material = Material(
        name=name,
        category=row["category"].strip().lower(),
        hardness_HB_min=_optional_float(row["hardness_HB_min"]),
        hardness_HB_max=_optional_float(row["hardness_HB_max"]),
        hardness_shore_A_min=_optional_float(row["hardness_shore_A_min"]),
        hardness_shore_A_max=_optional_float(row["hardness_shore_A_max"]),
        density_kg_m3=_optional_float(row["density_kg_m3"]),
        charpy_J=_optional_float(row["charpy_J"]),
        charpy_test_temp_C=_optional_float(row["charpy_test_temp_C"]),
        fracture_toughness_MPa_m05=_optional_float(row["fracture_toughness_MPa_m05"]),
        typical_applications=tuple(
            a.strip() for a in row["typical_applications"].split(";") if a.strip()
        ),
        source=row["source"].strip(),
        test_method=row["test_method"].strip(),
        source_quality=quality,
        data_status=row["data_status"].strip(),
        notes=row.get("notes", "").strip(),
    )
    _check_range(name, "hardness_HB", material.hardness_HB_min, material.hardness_HB_max)
    _check_range(
        name, "hardness_shore_A", material.hardness_shore_A_min, material.hardness_shore_A_max
    )
    if material.charpy_J is not None and material.charpy_test_temp_C is None:
        raise ValueError(f"{name!r}: charpy_J given without charpy_test_temp_C")
    return material


def _parse_wear_coefficient(row: dict[str, str]) -> WearCoefficient:
    name = row["material"].strip()
    wear_mode = row["wear_mode"].strip()
    coefficient_type = row["coefficient_type"].strip()
    _check_choice(name, "wear_mode", wear_mode, WEAR_MODES)
    _check_choice(name, "coefficient_type", coefficient_type, COEFFICIENT_TYPES)

    low = _optional_float(row["low"])
    typical = _optional_float(row["typical"])
    high = _optional_float(row["high"])
    present = [v for v in (low, typical, high) if v is not None]
    if present != sorted(present):
        raise ValueError(f"{name!r}: wear coefficients must satisfy low <= typical <= high")

    quality = row["source_quality"].strip().lower() or None
    source = row["source"].strip()
    if present and (quality is None or not source):
        raise ValueError(f"{name!r}: a published value needs source and source_quality")
    if quality is not None:
        _check_choice(name, "source_quality", quality, SOURCE_QUALITIES)

    return WearCoefficient(
        material=name,
        wear_mode=wear_mode,
        coefficient_type=coefficient_type,
        low=low,
        typical=typical,
        high=high,
        test_method=row["test_method"].strip(),
        source=source,
        source_quality=quality,
    )


def load_materials(path: str | Path | None = None) -> list[Material]:
    """Load materials from ``path``, or from the bundled CSV if omitted."""
    rows = _read_rows("materials.csv", path, {f.name for f in fields(Material)})
    return [_parse_material(row) for row in rows]


def load_wear_coefficients(path: str | Path | None = None) -> list[WearCoefficient]:
    """Load wear coefficients from ``path``, or from the bundled CSV if omitted."""
    rows = _read_rows("wear_coefficients.csv", path, {f.name for f in fields(WearCoefficient)})
    return [_parse_wear_coefficient(row) for row in rows]


def filter_by_category(materials: Iterable[Material], category: str) -> list[Material]:
    """Return materials whose category matches ``category`` (case-insensitive)."""
    wanted = category.strip().lower()
    return [m for m in materials if m.category == wanted]


def rank_by(materials: Iterable[Material], prop: str, descending: bool = True) -> list[Material]:
    """Rank materials by one numeric property.

    Materials with no value for ``prop`` are excluded, never treated as zero.
    """
    if prop not in NUMERIC_PROPERTIES:
        raise ValueError(f"cannot rank by {prop!r}; choose one of {NUMERIC_PROPERTIES}")
    with_value = [m for m in materials if getattr(m, prop) is not None]
    return sorted(with_value, key=lambda m: getattr(m, prop), reverse=descending)
