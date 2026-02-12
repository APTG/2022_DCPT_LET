# Treatment Plans
This directory contains plans for therapy.

- `plan01_sobp` SOBP for the three PMMA plate configurations.
- `plan02_mono` 160 MeV mono-energetic

# Ramped field descriptions made with RayStation

- Created using RayStation two ramped which overlapped will result in a flat SOBP.

## Plan 03 `ramp_full`
is a ramp across entire SOBP, starting at 100 % dose proximal edge, 0 % dose distal edge.

- `RD1.2.752.243.1.1.20250523160113556.3000.73252.dcm`  Dose distribution, total dose.
- `RD1.2.752.243.1.1.20250523160113556.4000.16653.dcm`  Dose distribution, Field 1.
- `RD1.2.752.243.1.1.20250523160113556.5000.84138.dcm`  Dose distribution, Field 2.
- `ramped_2Gy_ver2_full.dcm`  Spot data
- `RS1.2.752.243.1.1.20250522124652761.2000.43711.dcm`  Structure data

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

Corresponding easy-to-read `spotlist_*.dat` files are added for each plan.
