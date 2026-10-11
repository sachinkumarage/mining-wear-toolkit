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

## Scope of v0.1.0 (Day 1)

- `src/` layout package `minewear` (no runtime dependencies).
- A materials database, `src/minewear/data/materials.csv`, covering AR400,
  AR500, Hadfield manganese steel, Ni-Hard 4, high-chromium white iron,
  alumina ceramic, natural rubber and polyurethane.
- A loader (`minewear.materials`) with a `Material` dataclass and functions
  to load the database, filter by category and rank by a single numeric
  property.
- pytest tests for the loader.

Wear-life models and selection logic are not in this release.

```python
from minewear import load_materials, filter_by_category, rank_by

materials = load_materials()
white_irons = filter_by_category(materials, "white_iron")
for m in rank_by(materials, "hardness_HB"):
    print(m.name, m.hardness_HB)
```

`rank_by` skips materials that have no value for the property. A blank is
never treated as zero.

## Database columns

| Column | Meaning |
|---|---|
| `name` | Material name |
| `category` | `steel`, `white_iron`, `ceramic` or `elastomer` |
| `hardness_HB` | Brinell hardness (metals). Lower bound of the published range unless `notes` says otherwise |
| `hardness_shore_A` | Shore A hardness (elastomers) |
| `density_kg_m3` | Density, kg/m³ |
| `typical_applications` | `;`-separated list taken from the source |
| `impact_resistance` | `low` / `med` / `high`, only where a source supports it |
| `relative_cost_index` | Relative cost (blank for every row in v0.1.0) |
| `data_status` | `indicative` for every row |
| `source` | Reference for the values in the row |
| `notes` | Full published ranges, test conditions and caveats |

Brinell and Shore A are kept in separate columns because they are different
scales and cannot be compared or ranked together. Brinell does not apply to
technical ceramics, so alumina has no hardness value; its notes give the
published Knoop value instead.

## Limitation: indicative data, screening only

**Every value in the database is indicative and is for screening only.** It is
not suitable for design, procurement or warranty decisions.

- Values come from published standards summaries, reference texts and supplier
  datasheets. Each row names its source. Suppliers' figures are typical
  values, not guaranteed minimums, and they vary with grade, section thickness,
  heat treatment and test method.
- Where no published value was found, the field is **blank** rather than
  estimated. In v0.1.0 that includes density for AR400, AR500 and Ni-Hard 4,
  most `impact_resistance` ratings, and every `relative_cost_index`.
- For any engineering decision, use the governing standard (for example
  ASTM A532 or ASTM A128), the mill or foundry certificate, and the current
  supplier datasheet for the exact product.

## Development

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```

## License

MIT. See [LICENSE](LICENSE).
