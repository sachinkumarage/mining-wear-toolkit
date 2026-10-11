# mining-wear-toolkit (`minewear`)

An open-source toolkit for estimating wear life and selecting wear-resistant
materials for mining and mineral processing equipment: liners, chutes, slurry
pumps and crusher parts. It is written for materials engineers and maintenance
engineers.

## The engineering problem

Wear parts are among the biggest recurring maintenance costs in a mine or
concentrator. Liners, chute plates, pump wet-ends and crusher wear parts are
consumed continuously by sliding abrasion, impact and erosion. Choosing a
material means trading off hardness, toughness, density and cost against the
wear mode at each location, which is often done from scattered supplier
datasheets and rules of thumb. Unplanned failures stop production. Over-
specified materials waste money.

`minewear` aims to put the material data and wear-life estimates in one
transparent, testable place, with every number traceable to its source.

## Day 1 scope (v0.1.x)

- `src/` layout package `minewear` (no runtime dependencies).
- `data/materials.csv`: AR400, AR500, Hadfield manganese steel, Ni-Hard 4,
  high-chromium white iron, alumina ceramic, natural rubber and polyurethane.
- `data/wear_coefficients.csv`: published wear figures by material and wear
  mode, with gaps left blank.
- `data/site_wear_rates_template.csv`: header-only template for recording
  measured wear on site.
- Loaders: `load_materials()`, `load_wear_coefficients()`,
  `filter_by_category()` and `rank_by()`.
- pytest tests.

Wear-life models and selection logic are not in this release.

```python
from minewear import load_materials, load_wear_coefficients, rank_by

materials = load_materials()
for m in rank_by(materials, "hardness_HB_min"):
    print(m.name, m.hardness_HB_min, m.hardness_HB_max, m.source_quality)

coefficients = load_wear_coefficients()
```

`rank_by` skips materials that have no value for the property. A blank is
never treated as zero.

## Data quality levels

Every material row, and every wear coefficient that has a value, carries a
`source_quality`:

| Level | Meaning |
|---|---|
| `primary` | A standard, or a producer's own data sheet for the material |
| `secondary` | Reference site, encyclopaedia or supplier summary |
| `unverified` | Known only from a search result; the source could not be opened |

All data is also marked `data_status = indicative`. A `primary` value is still
only a typical value for one producer's product, not a guaranteed minimum.
[docs/DATA_TODO.md](docs/DATA_TODO.md) lists every blank or non-primary value
and a suggested primary source to check.

## Materials columns

| Column | Meaning |
|---|---|
| `name`, `category` | Category is `steel`, `white_iron`, `ceramic` or `elastomer` |
| `hardness_HB_min`, `hardness_HB_max` | Published Brinell range (metals) |
| `hardness_shore_A_min`, `hardness_shore_A_max` | Published Shore A range (elastomers) |
| `density_kg_m3` | From a grade-specific data sheet only; never a generic value |
| `charpy_J`, `charpy_test_temp_C` | Charpy V-notch energy and test temperature (steels) |
| `fracture_toughness_MPa_m05` | K_Ic in MPa·m^0.5 (ceramics and white irons) |
| `typical_applications` | `;`-separated list taken from the source |
| `source`, `test_method` | Reference, and the test method and conditions it states |
| `source_quality`, `data_status` | See above |
| `notes` | Original units, conversions and caveats |

A single published value is stored with min = max. Brinell and Shore A are
separate columns because they are different scales. Units are SI; imperial
values are converted and the original is recorded in `notes`.

## Wear coefficient columns

`material`, `wear_mode` (`two_body_abrasion`, `three_body_abrasion`,
`slurry_erosion`), `coefficient_type`, `low`, `typical`, `high`, `test_method`,
`source`, `source_quality`.

Coefficient types: `dimensionless_k`, `specific_wear_rate_mm3_per_Nm`,
`astm_g65_volume_loss_mm3` and `iso4649_volume_loss_mm3`. The last is used
for elastomers, which rarely have ASTM G65 data. Results from different test
methods are not comparable. A value published only as a maximum is stored in
`high`, with `low` and `typical` blank.

## Limitation: indicative data, screening only

**Every value is indicative and is for screening only.** It is not suitable
for design, procurement or warranty decisions. Values vary with grade, section
thickness, heat treatment and test method. Where no published value was found
the field is blank rather than estimated. For any engineering decision, use the
governing standard (for example ASTM A532 or ASTM A128), the mill or foundry
certificate, and the current data sheet for the exact product.

## Development

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/ruff check .
.venv/bin/pytest
```

## License

MIT. See [LICENSE](LICENSE).
