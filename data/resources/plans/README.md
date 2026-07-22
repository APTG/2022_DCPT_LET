# Treatment Plans
This directory contains plans for therapy.

- `plan01_sobp` SOBP for the three PMMA plate configurations.
- `plan02_mono` 160 MeV mono-energetic
- `plan05_sobp_3d` SOBP, isocenter at 7.28 cm (WET 7.5 cm), detector at 9.42 cm depth (WET 9.6 cm) (clinical name: SOBP 3d)
- `plan06_sobp_4d` SOBP, isocenter at 4.37 cm (WET 4.5 cm), detector at 6.42 cm depth (WET 6.5 cm) (clinical name: SOBP 4d, 3 cm range shifter)
- `plan07_sobp_5d` SOBP, isocenter at 8.25 cm (WET 8.5 cm), detector at 14.26 cm depth (WET 14.5 cm) (clinical name: SOBP 5d, 3 cm range shifter)

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

**Coordinate convention:** X/Y spot positions are at the **iso-center plane**. All beam model parameters (spot size FWHM, divergence, correlation) are defined at the **beam model plane** (upstream of iso-center).

The filename encodes the beam model version and the number of beam model components:
- `spotlist_BMv2_c7*.dat`: **reduced beam model** (7 components), beam model plane at **50 cm upstream** from iso-center. Plans 01–04 only.
- `spotlist_BMv2_c11*.dat`: **full beam model** (11 components), beam model plane at **50 cm upstream** from iso-center. Plans 01–04 only.
- `spotlist_BMv5_c7*.dat`: **reduced beam model** (7 components), beam model plane at **60 cm upstream** from iso-center. All plans.
- `spotlist_BMv5_c11*.dat`: **full beam model** (11 components), beam model plane at **60 cm upstream** from iso-center. All plans.

# 2026 Measurement Campaign Plans

Plans from the 2026 LET commissioning session at DCPT. All are SOBPs with detectors placed at different depths. A 3 cm LEXAN range shifter was used for plans 06 and 07 and is modelled explicitly in the simulation geometry.

## Plan 05 `sobp_3d`
Clinical name: SOBP 3d. Single-field SOBP with isocenter at 7.28 cm depth (WET 7.5 cm), detector at 9.42 cm depth (WET 9.6 cm).
- Max spot energy: 120.2 MeV
- Geometry E (see `docs/geometry.md`)

## Plan 06 `sobp_4d`
Clinical name: SOBP 4d. Single-field SOBP with isocenter at 4.37 cm depth (WET 4.5 cm), detector at 6.42 cm depth (WET 6.5 cm). 3 cm LEXAN range shifter at 13.59 cm from isocenter.
- Max spot energy: 126.5 MeV
- Geometry F (see `docs/geometry.md`)

## Plan 07 `sobp_5d`
Clinical name: SOBP 5d. Single-field SOBP with isocenter at 8.25 cm depth (WET 8.5 cm), detector at 14.26 cm depth (WET 14.5 cm). 3 cm LEXAN range shifter at 17.38 cm from isocenter.
- Max spot energy: 172.1 MeV
- Geometry G (see `docs/geometry.md`)
