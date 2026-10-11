import pytest

from minewear import (
    SOURCE_QUALITIES,
    Material,
    filter_by_category,
    load_materials,
    rank_by,
)

HEADER = (
    "name,category,hardness_HB_min,hardness_HB_max,hardness_shore_A_min,"
    "hardness_shore_A_max,density_kg_m3,charpy_J,charpy_test_temp_C,"
    "fracture_toughness_MPa_m05,typical_applications,source,test_method,"
    "source_quality,data_status,notes\n"
)


def _row(**overrides):
    values = {
        "name": "Test plate",
        "category": "steel",
        "hardness_HB_min": "",
        "hardness_HB_max": "",
        "hardness_shore_A_min": "",
        "hardness_shore_A_max": "",
        "density_kg_m3": "",
        "charpy_J": "",
        "charpy_test_temp_C": "",
        "fracture_toughness_MPa_m05": "",
        "typical_applications": "",
        "source": "ref",
        "test_method": "method",
        "source_quality": "primary",
        "data_status": "indicative",
        "notes": "",
    }
    values.update(overrides)
    return ",".join(values.values()) + "\n"


def _write(tmp_path, *rows):
    csv_file = tmp_path / "m.csv"
    csv_file.write_text(HEADER + "".join(rows))
    return csv_file


@pytest.fixture(scope="module")
def materials():
    return load_materials()


@pytest.fixture(scope="module")
def by_name(materials):
    return {m.name: m for m in materials}


def test_bundled_database_has_all_day1_materials(materials):
    assert {m.name for m in materials} == {
        "AR400",
        "AR500",
        "Hadfield manganese steel",
        "Ni-Hard 4",
        "High-chromium white iron",
        "Alumina ceramic",
        "Natural rubber",
        "Polyurethane",
    }
    assert all(isinstance(m, Material) for m in materials)


def test_every_row_is_indicative_sourced_and_classified(materials):
    for m in materials:
        assert m.data_status == "indicative"
        assert m.source
        assert m.test_method
        assert m.source_quality in SOURCE_QUALITIES


def test_source_quality_assignments(by_name):
    # AR400/AR500 moved from an encyclopaedia to producer datasheets in v0.1.1.
    assert by_name["AR400"].source_quality == "primary"
    assert by_name["AR500"].source_quality == "primary"
    assert "wikipedia" not in by_name["AR400"].source.lower()
    assert "wikipedia" not in by_name["AR500"].source.lower()
    # The Hadfield source page is offline, so its value rests on a search result.
    assert by_name["Hadfield manganese steel"].source_quality == "unverified"


def test_hardness_ranges_match_published_values(by_name):
    # Read directly from the cited datasheets.
    assert (by_name["AR400"].hardness_HB_min, by_name["AR400"].hardness_HB_max) == (360, 444)
    assert (by_name["AR500"].hardness_HB_min, by_name["AR500"].hardness_HB_max) == (470, 535)
    hcwi = by_name["High-chromium white iron"]
    assert (hcwi.hardness_HB_min, hcwi.hardness_HB_max) == (600, 700)
    pu = by_name["Polyurethane"]
    assert (pu.hardness_shore_A_min, pu.hardness_shore_A_max) == (55, 95)


def test_min_never_exceeds_max(materials):
    for m in materials:
        for lo, hi in (
            (m.hardness_HB_min, m.hardness_HB_max),
            (m.hardness_shore_A_min, m.hardness_shore_A_max),
        ):
            if lo is not None and hi is not None:
                assert lo <= hi


def test_ar400_charpy_converted_to_si(by_name):
    # Published: 25 ft-lb at -40 F. Hand calculation: 25 * 1.355818 = 33.895 J,
    # and -40 F = (-40 - 32) * 5/9 = -40 C.
    ar400 = by_name["AR400"]
    assert ar400.charpy_J == pytest.approx(33.9, abs=0.05)
    assert ar400.charpy_test_temp_C == -40


def test_toughness_columns_by_category(by_name):
    assert by_name["AR500"].charpy_J == 38
    assert by_name["Alumina ceramic"].fracture_toughness_MPa_m05 == 4
    assert by_name["Alumina ceramic"].charpy_J is None
    # No published Charpy or K_Ic was found for these; they must stay blank.
    assert by_name["Hadfield manganese steel"].charpy_J is None
    assert by_name["Ni-Hard 4"].fracture_toughness_MPa_m05 is None


def test_blank_values_load_as_none(by_name):
    alumina = by_name["Alumina ceramic"]
    assert alumina.hardness_HB_min is None
    assert alumina.hardness_shore_A_min is None
    assert alumina.density_kg_m3 == 3900
    assert by_name["AR400"].density_kg_m3 is None


def test_no_generic_steel_density(materials):
    for m in filter_by_category(materials, "steel"):
        assert m.density_kg_m3 != 7850


def test_removed_columns_are_gone():
    names = {f for f in Material.__dataclass_fields__}
    assert "relative_cost_index" not in names
    assert "impact_resistance" not in names


def test_elastomers_use_shore_a_not_brinell(materials):
    for m in filter_by_category(materials, "elastomer"):
        assert m.hardness_HB_min is None
        assert m.hardness_shore_A_min is not None


def test_applications_are_split_into_tuple(by_name):
    apps = by_name["High-chromium white iron"].typical_applications
    assert isinstance(apps, tuple)
    assert "slurry pumps" in apps


def test_filter_by_category_is_case_insensitive(materials):
    steels = filter_by_category(materials, " Steel ")
    assert {m.name for m in steels} == {"AR400", "AR500", "Hadfield manganese steel"}


def test_filter_by_unknown_category_returns_empty(materials):
    assert filter_by_category(materials, "unobtainium") == []


def test_rank_by_descending_excludes_missing_values(materials):
    ranked = rank_by(materials, "hardness_HB_min")
    assert [m.hardness_HB_min for m in ranked] == [600, 600, 470, 360, 200]
    assert "Alumina ceramic" not in {m.name for m in ranked}


def test_rank_by_ascending(materials):
    ranked = rank_by(materials, "density_kg_m3", descending=False)
    assert [m.name for m in ranked] == [
        "Natural rubber",
        "Polyurethane",
        "Alumina ceramic",
        "High-chromium white iron",
    ]


def test_rank_by_rejects_non_numeric_property(materials):
    with pytest.raises(ValueError, match="cannot rank by"):
        rank_by(materials, "name")


def test_load_from_custom_path(tmp_path):
    csv_file = _write(
        tmp_path,
        _row(
            hardness_HB_min="450",
            hardness_HB_max="500",
            charpy_J="30",
            charpy_test_temp_C="-20",
            source_quality="Secondary",
            typical_applications="chutes;liners",
        ),
    )
    [m] = load_materials(csv_file)
    assert (m.hardness_HB_min, m.hardness_HB_max) == (450, 500)
    assert (m.charpy_J, m.charpy_test_temp_C) == (30, -20)
    assert m.source_quality == "secondary"
    assert m.typical_applications == ("chutes", "liners")


def test_invalid_source_quality_raises(tmp_path):
    with pytest.raises(ValueError, match="source_quality"):
        load_materials(_write(tmp_path, _row(source_quality="guess")))


def test_min_above_max_raises(tmp_path):
    with pytest.raises(ValueError, match="exceeds max"):
        load_materials(_write(tmp_path, _row(hardness_HB_min="500", hardness_HB_max="400")))


def test_charpy_without_temperature_raises(tmp_path):
    with pytest.raises(ValueError, match="charpy_test_temp_C"):
        load_materials(_write(tmp_path, _row(charpy_J="30")))


def test_missing_column_raises(tmp_path):
    csv_file = tmp_path / "m.csv"
    csv_file.write_text("name,category\nX,steel\n")
    with pytest.raises(ValueError, match="missing columns"):
        load_materials(csv_file)
