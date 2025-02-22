# Treatment Plans
This directory contains plans for therapy.

- `plan01_sobp` SOBP for the three PMMA plate configurations.
- `plan02_mono` 160 MeV mono-energetic

# Ramped field descriptions made with RayStation

- Created using RayStation one flat SOBP, and two ramped which overlapped will result in a flat SOBP.
- Kindly provided by Erik Traneus.
- Beam model is not the final one, so the ramped fileds are only preliminary.

## Plan 03 `sobp_raystation`
is a flat SOBP, just for test purposes

- `RD1.2.752.243.1.1.20221209141208883.1000.23750.dcm`  Dose distribution, RayStation
- `RP1.2.752.243.1.1.20221209141208883.9000.73261.dcm`  Spot data
- `RS1.2.752.243.1.1.20221209135909128.2180.16718.dcm`  Structure data

## Plan 04 `ramp_10cm`
is a ramp across entire SOBP, starting at 100 % dose proximal edge, 0 % dose distal edge.

- `RD1.2.752.243.1.1.20221209141404014.2400.81587.dcm`  Dose distribution, RayStation
- `RP1.2.752.243.1.1.20221209141404013.2300.75558.dcm`  Spot data
- `RS1.2.752.243.1.1.20221209135909128.2180.16718.dcm`  Structure data

## Plan 05 `ramp_4cm`
is a special ramp:
- in PTV it starts at 100 % dose, and being flat for 3 cm.
- Then follows a 4 cm ramp starting at 90 % dose, stopping at 10 % dose,
- Finally a 3 cm flat section follows at 0 % dose.

- `RD1.2.752.243.1.1.20221209140939394.3000.60527.dcm`  Dose distribution, RayStation
- `RP1.2.752.243.1.1.20221209140939393.2000.36612.dcm`  Spot data
- `RS1.2.752.243.1.1.20221209135909128.2180.16718.dcm`  Structure data

Corresponding easy-to-read `spotlist_*.dat` files are added for each plan.
