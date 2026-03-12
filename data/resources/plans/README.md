# Treatment Plans
This directory contains plans for therapy.

- `plan01_sobp` SOBP for the three PMMA plate configurations.
- `plan02_mono` 160 MeV mono-energetic
- `plan05_sobp_3d` SOBP, isocenter at 7.5 cm, detector at 9.6 cm depth (clinical name: SOBP 3d)
- `plan06_sobp_4d` SOBP, isocenter at 4.5 cm, detector at 6.5 cm depth (clinical name: SOBP 4d, 3 cm range shifter)
- `plan07_sobp_5d` SOBP, isocenter at 8.5 cm, detector at 14.5 cm depth (clinical name: SOBP 5d, 3 cm range shifter)

# Ramped field descriptions made with RayStation

- Created using RayStation two ramped which overlapped will result in a flat SOBP.
- We provide DICOM files in two dataformats, one native for RayStation, and one exported from RayStation, in a mode compatible with Eclipse TPS.

## Plan 03 `ramp_full`
is a ramp across entire SOBP, starting at 100 % dose proximal edge, 0 % dose distal edge.

- `RD1.2.752.243.1.1.20250523160113556.3000.73252.dcm`  Dose distribution, total dose.
- `RD1.2.752.243.1.1.20250523160113556.4000.16653.dcm`  Dose distribution, Field 1.
- `RD1.2.752.243.1.1.20250523160113556.5000.84138.dcm`  Dose distribution, Field 2.
- `ramped_2Gy_ver2_full.dcm`  Spot data
- `RS1.2.752.243.1.1.20250522124652761.2000.43711.dcm`  Structure data

The complete DICOM study, including CT data is available at [Plan03_Eclipse.zip](https://s3.cloud.cyfronet.pl/2022_dcpt_let/plans/Plan03_Eclipse.zip) and [Plan03_RayStation.zip](https://s3.cloud.cyfronet.pl/2022_dcpt_let/plans/Plan03_RayStation.zip)

## Plan 04 `ramp_middle`
is a special ramp:
- in PTV it starts at 100 % dose, and being flat for a few cm.
- Then follows a ~4 cm ramp starting at 90 % dose, stopping at 10 % dose,
- Finally a few cm flat section follows at 0 % dose.

- `RD1.2.752.243.1.1.20250522124652830.4000.14613.dcm`  Dose distribution, total dose.
- `RD1.2.752.243.1.1.20250522124652830.5000.68878.dcm`  Dose distribution, Field 1.
- `RD1.2.752.243.1.1.20250522124652830.6000.18286.dcm`  Dose distribution, Field 2.
- `ramped_2Gy_ver1_middel.dcm`  Spot data
- `RS1.2.752.243.1.1.20250522124652761.2000.43711.dcm`  Structure data

The complete DICOM study, including CT data is available at - [Plan04_Eclipse.zip](https://s3.cloud.cyfronet.pl/2022_dcpt_let/plans/Plan04_Eclipse.zip) and [Plan04_RayStation.zip](https://s3.cloud.cyfronet.pl/2022_dcpt_let/plans/Plan04_RayStation.zip)

## Spotlists
Corresponding easy-to-read spotlist files are added for each plan.
These are made with spotpositions at isocenter, with reduced beam model.

- `spotlist_*.dat` : spotlist with positions at **isocenter** and **reduced beam model**, set at **beam model plane** (50.0 cm upstream)
- `spotlist_c7*.dat`: spotlist with positions at **beam model plane** and **reduced beam model**, set at **beam model plane** (50.0 cm upstream)
- `spotlist_c11*.dat`: spotlist with positions at **beam model plane** and **full beam model**, set at **beam model plane** (50.0 cm upstream)

# 2026 Measurement Campaign Plans

Plans from the 2026 LET commissioning session at DCPT. All are SOBPs with detectors placed at different depths. A 3 cm range shifter was used for plans 06 and 07.

## Plan 05 `sobp_3d`
Clinical name: SOBP 3d. Single-field SOBP with isocenter at 7.5 cm depth, detector at 9.6 cm depth.
- Max spot energy: 120.2 MeV
- Geometry E (see `docs/geometry.md`)

## Plan 06 `sobp_4d`
Clinical name: SOBP 4d. Single-field SOBP with isocenter at 4.5 cm depth, detector at 6.5 cm depth. 3 cm range shifter used.
- Max spot energy: 126.5 MeV
- Geometry F (see `docs/geometry.md`)

## Plan 07 `sobp_5d`
Clinical name: SOBP 5d. Single-field SOBP with isocenter at 8.5 cm depth, detector at 14.5 cm depth. 3 cm range shifter used.
- Max spot energy: 172.1 MeV
- Geometry G (see `docs/geometry.md`)
