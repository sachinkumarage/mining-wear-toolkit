import pytest

from minewear import (
    Material,
    filter_by_category,
    load_materials,
    rank_by,
)

HEADER = (
    "name,category,hardness_HB,hardness_shore_A,density_kg_m3,"
    "typical_applications,impact_resistance,relative_cost_index,"
    "data_status,source,notes\n"
)


@pytest.fixture(scope="module")
def materials():
    return load_materials()


def test_bundled_database_has_all_day1_materials(materials):
    names = {m.name for m in materials}
    assert names == {
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


def test_every_row_is_indicative_and_sourced(materials):
    for m in materials:
        assert m.data_status == "indicative"
        assert m.source


def test_blank_values_load_as_none(materials):
    alumina = next(m for m in materials if m.name == "Alumina ceramic")
    assert alumina.hardness_HB is None
    assert alumina.relative_cost_index is None
    assert alumina.density_kg_m3 == 3900


def test_elastomers_use_shore_a_not_brinell(materials):
    for m in filter_by_category(materials, "elastomer"):
        assert m.hardness_HB is None
        assert m.hardness_shore_A is not None


def test_applications_are_split_into_tuple(materials):
    hcwi = next(m for m in materials if m.name == "High-chromium white iron")
    assert "slurry pumps" in hcwi.typical_applications
    assert isinstance(hcwi.typical_applications, tuple)


def test_filter_by_category_is_case_insensitive(materials):
    steels = filter_by_category(materials, " Steel ")
    assert {m.name for m in steels} == {
        "AR400",
        "AR500",
        "Hadfield manganese steel",
    }


def test_filter_by_unknown_category_returns_empty(materials):
    assert filter_by_category(materials, "unobtainium") == []


def test_rank_by_descending_excludes_missing_values(materials):
    ranked = rank_by(materials, "hardness_HB")
    values = [m.hardness_HB for m in ranked]
    assert values == sorted(values, reverse=True)
    assert all(v is not None for v in values)
    assert "Alumina ceramic" not in {m.name for m in ranked}


def test_rank_by_ascending(materials):
    ranked = rank_by(materials, "density_kg_m3", descending=False)
    assert ranked[0].name == "Natural rubber"


def test_rank_by_rejects_non_numeric_property(materials):
    with pytest.raises(ValueError, match="cannot rank by"):
        rank_by(materials, "name")


def test_load_from_custom_path(tmp_path):
    csv_file = tmp_path / "m.csv"
    csv_file.write_text(
        HEADER + "Test plate,steel,450,,7850,chutes;liners,MED,,indicative,ref,\n"
    )
    [m] = load_materials(csv_file)
    assert m.hardness_HB == 450
    assert m.impact_resistance == "med"
    assert m.typical_applications == ("chutes", "liners")


def test_invalid_impact_level_raises(tmp_path):
    csv_file = tmp_path / "m.csv"
    csv_file.write_text(HEADER + "Bad,steel,,,,,extreme,,indicative,ref,\n")
    with pytest.raises(ValueError, match="impact_resistance"):
        load_materials(csv_file)


def test_missing_column_raises(tmp_path):
    csv_file = tmp_path / "m.csv"
    csv_file.write_text("name,category\nX,steel\n")
    with pytest.raises(ValueError, match="missing columns"):
        load_materials(csv_file)
