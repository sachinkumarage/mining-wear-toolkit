# Data TODO

Every blank or non-primary value in the bundled data, what is missing, and a
suggested primary source to check. Blank fields are deliberate: no value is
entered until a published reference supports it.

Not applicable by design (not listed below): Brinell hardness for ceramics and
elastomers, Shore A for metals and ceramics, Charpy energy for white irons,
ceramics and elastomers, and fracture toughness for steels and elastomers.

## materials.csv

| Material | Field | Status | What is missing | Suggested primary source |
|---|---|---|---|---|
| AR400 | density_kg_m3 | blank | SSAB AR400F data sheet (2017-04-19) gives no density | SSAB technical support or a current AR400F data sheet revision that includes physical properties |
| AR400 | charpy_J | primary, typical only | Typical (not guaranteed) value for 19 mm plate, converted from 25 ft-lb | Mill certificate with guaranteed CVN for the ordered thickness |
| AR500 | density_kg_m3 | blank | CMC TruWEAR AR500F sheet gives no density | CMC Impact Metals technical data on request |
| AR500 | typical_applications | blank | Producer lists industries (mining, asphalt, concrete, aggregate), not components | Another AR500 producer data sheet that lists applications |
| AR500 | charpy_J | primary, information only | Not tested unless specified at order | Mill certificate with CVN specified at order |
| Hadfield manganese steel | whole row | unverified | Cited page (metallographic.com) was offline on 2026-10-12; 200 HB as-cast known only from a search-result summary | ASTM A128/A128M (current revision); a manganese-steel foundry data sheet; ASM Handbook Vol. 1, austenitic manganese steels |
| Hadfield manganese steel | density_kg_m3, charpy_J, charpy_test_temp_C, typical_applications | blank | No grade-specific published values found | As above |
| Ni-Hard 4 | density_kg_m3 | blank | Wilfley sheet gives no density | Nickel Institute publication 11017, *Properties and applications of Ni-Hard alloys* (returned HTTP 403 when checked) |
| Ni-Hard 4 | fracture_toughness_MPa_m05 | blank | No producer data sheet value found | ASM Alloy Digest CI-34 (Ni-Hard Type 4); Nickel Institute publication 11017 |
| Ni-Hard 4 | hardness_HB_min/max | primary | Range is the supplier's average hardness, not the ASTM A532 Class I Type D minimum | ASTM A532/A532M hardness table |
| High-chromium white iron | fracture_toughness_MPa_m05 | blank | No producer data sheet value found | Foundry data sheet with K_Ic; Pariente et al., *Mechanical strength and fracture toughness of high chromium white cast irons* (2008) as a cross-check |
| High-chromium white iron | hardness_HB_min/max | primary | Foundry range for hardened condition, varies with section thickness | ASTM A532/A532M Class III Type A hardness table |
| Alumina ceramic | typical_applications | blank | CoorsTek chart is not application-specific | CoorsTek or other producer wear-ceramic (mining liner) brochure |
| Alumina ceramic | fracture_toughness_MPa_m05 | primary, lower bound | Published as 4-5 MPa.m^0.5; 4 stored | Producer data sheet with a single value and test method (e.g. ASTM C1421) |
| Natural rubber | hardness_shore_A_min/max | primary | Brochure gives 60 Shore A with no tolerance; stored as min = max | Trelleborg BLACKROCK PLUS technical data sheet with tolerance |
| Natural rubber | density_kg_m3 | primary | Specific gravity 1.12 given without test method | Trelleborg technical data sheet with ISO 2781 or equivalent |
| Polyurethane | density_kg_m3 | primary, interpreted | Printed as "1.210 Kg/m3" and described as approximate; read as 1210 kg/m3 | NUBA technical data sheet for a specific grade, or Weir Linathane data sheet |
| Polyurethane | hardness_shore_A_min/max | primary | 55-95 Shore A is the possible formulation range, not one grade | Grade-specific technical data sheet |

## wear_coefficients.csv

| Material | Field | Status | What is missing | Suggested primary source |
|---|---|---|---|---|
| AR400, AR500, Hadfield manganese steel, Ni-Hard 4, High-chromium white iron, Alumina ceramic | astm_g65_volume_loss_mm3 (low, typical, high) | blank | No producer-published ASTM G65 procedure A volume loss found | Producer G65 test reports (SSAB, CMC Impact Metals, Wilfley, Penticton Foundry, CoorsTek); ASM Handbook Vol. 18 |
| Natural rubber | iso4649_volume_loss_mm3 | primary, maximum only | Published as a limit (<= 90 mm3 at 10 N); low and typical blank | Trelleborg test report with measured values |
| Polyurethane | iso4649_volume_loss_mm3 | primary, maximum only | Published as a maximum (12 mm3, polyester system); load not stated | NUBA technical data sheet with test load |
| All materials | slurry_erosion (any coefficient type) | no rows | No published slurry-erosion coefficients found | Pump producer wear data (e.g. Weir Minerals); ASTM G75 (slurry abrasivity) test reports |
| All materials | dimensionless_k, specific_wear_rate_mm3_per_Nm | no rows | No published values found | ASM Handbook Vol. 18; peer-reviewed tribology data with stated test conditions |

`iso4649_volume_loss_mm3` was added as a coefficient type because ASTM G65 is
rarely published for elastomers, and ISO 4649 is their most commonly published
abrasion figure. ISO 4649 and ASTM G65 results are not comparable with each other.
