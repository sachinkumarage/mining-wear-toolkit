import csv
from importlib import resources

import pytest

from minewear import (
    COEFFICIENT_TYPES,
    SOURCE_QUALITIES,
    WEAR_MODES,
    WearCoefficient,
    load_materials,
    load_wear_coefficients,
)

HEADER = "material,wear_mode,coefficient_type,low,typical,high,test_method,source,source_quality\n"


def _write(tmp_path, row):
    csv_file = tmp_path / "w.csv"
    csv_file.write_text(HEADER + row + "\n")
    return csv_file


@pytest.fixture(scope="module")
def coefficients():
    return load_wear_coefficients()


def test_bundled_rows_load(coefficients):
    assert len(coefficients) == 8
    assert all(isinstance(c, WearCoefficient) for c in coefficients)


def test_modes_and_types_are_valid(coefficients):
    for c in coefficients:
        assert c.wear_mode in WEAR_MODES
        assert c.coefficient_type in COEFFICIENT_TYPES
        assert c.test_method


def test_every_coefficient_material_exists_in_materials_db(coefficients):
    names = {m.name for m in load_materials()}
    assert {c.material for c in coefficients} <= names


def test_published_values_have_primary_or_classified_source(coefficients):
    for c in coefficients:
        if any(v is not None for v in (c.low, c.typical, c.high)):
            assert c.source
            assert c.source_quality in SOURCE_QUALITIES


def test_blank_values_load_as_none(coefficients):
    ar400 = next(c for c in coefficients if c.material == "AR400")
    assert ar400.coefficient_type == "astm_g65_volume_loss_mm3"
    assert (ar400.low, ar400.typical, ar400.high) == (None, None, None)
    assert ar400.source == ""
    assert ar400.source_quality is None


def test_published_maximum_stored_as_high_only(coefficients):
    # Trelleborg BLACKROCK PLUS: ISO 4649 dry abrasion loss <= 90 mm3 at 10 N.
    nr = next(c for c in coefficients if c.material == "Natural rubber")
    assert (nr.low, nr.typical, nr.high) == (None, None, 90)
    assert nr.wear_mode == "two_body_abrasion"


def test_custom_row_parses_all_values(tmp_path):
    [c] = load_wear_coefficients(
        _write(tmp_path, "X,slurry_erosion,dimensionless_k,1e-5,2e-5,4e-5,m,ref,secondary")
    )
    assert (c.low, c.typical, c.high) == (1e-5, 2e-5, 4e-5)
    assert c.source_quality == "secondary"


def test_unknown_wear_mode_raises(tmp_path):
    with pytest.raises(ValueError, match="wear_mode"):
        load_wear_coefficients(_write(tmp_path, "X,fretting,dimensionless_k,,,,m,,"))


def test_unknown_coefficient_type_raises(tmp_path):
    with pytest.raises(ValueError, match="coefficient_type"):
        load_wear_coefficients(_write(tmp_path, "X,slurry_erosion,mass_loss_g,,,,m,,"))


def test_unordered_values_raise(tmp_path):
    with pytest.raises(ValueError, match="low <= typical <= high"):
        load_wear_coefficients(
            _write(tmp_path, "X,slurry_erosion,dimensionless_k,3,2,4,m,ref,primary")
        )


def test_value_without_source_raises(tmp_path):
    with pytest.raises(ValueError, match="needs source"):
        load_wear_coefficients(
            _write(tmp_path, "X,three_body_abrasion,astm_g65_volume_loss_mm3,,50,,m,,")
        )


def test_site_wear_rates_template_is_header_only():
    text = resources.files("minewear").joinpath("data", "site_wear_rates_template.csv")
    rows = list(csv.reader(text.read_text(encoding="utf-8").splitlines()))
    assert rows == [
        [
            "component",
            "material",
            "measured_thickness_loss_mm",
            "tonnes_processed",
            "operating_hours",
            "date_from",
            "date_to",
            "notes",
        ]
    ]
