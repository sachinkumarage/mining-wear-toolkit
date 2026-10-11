# Changelog

All notable changes to this project are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## [0.1.1] - 2026-10-12

### Added
- `wear_coefficients.csv` with `WearCoefficient` dataclass and
  `load_wear_coefficients()`. Wear modes: two-body abrasion, three-body abrasion,
  slurry erosion. Coefficient types: dimensionless k, specific wear rate,
  ASTM G65 volume loss, ISO 4649 volume loss.
- `site_wear_rates_template.csv` (header only) for recording measured site wear.
- `source_quality` column (primary / secondary / unverified) and `test_method`
  column for every material row.
- Toughness columns: `charpy_J`, `charpy_test_temp_C` (steels) and
  `fracture_toughness_MPa_m05` (ceramics and white irons).
- `docs/DATA_TODO.md` listing every blank or non-primary value.

### Changed
- Hardness is now stored as the full published range: `hardness_HB_min/max`
  and `hardness_shore_A_min/max`.
- AR400 and AR500 now cite producer data sheets (SSAB AR400F, CMC TruWEAR
  AR500F) instead of an encyclopaedia. AR500 range is now 470-535 HBW.
- Natural rubber now cites Trelleborg's mining sheet-rubber brochure
  (BLACKROCK PLUS, 1120 kg/m3).
- Polyurethane now cites a mining screen-panel data sheet (NUBA) instead of a
  general-purpose plate.
- Hadfield manganese steel marked `unverified`: its source page is offline.

### Removed
- `relative_cost_index` (costs will be user inputs in a later version).
- `impact_resistance` (replaced by numeric toughness columns).
- Densities not backed by a grade-specific data sheet (Hadfield manganese steel).

## [0.1.0] - 2026-10-11

### Added
- `minewear` package (src layout), MIT license.
- Materials database for AR400, AR500, Hadfield manganese steel, Ni-Hard 4,
  high-chromium white iron, alumina ceramic, natural rubber and polyurethane.
- `Material` dataclass with `load_materials()`, `filter_by_category()` and
  `rank_by()`.
- pytest tests for the loader.
