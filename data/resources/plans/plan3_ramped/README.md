# Ramped field descriptions

- Fields are similar to plan 1, but created using RayStation and are ramped.
- Kindly provided by Erik Traneus.

Plan names are subject to change.

## Plan 3i `refrence`
- is a flat SOBP, just for test purposes

`RD1.2.752.243.1.1.20221206151952575.1000.46040.dcm`  Dose distribution, RayStation
`RP1.2.752.243.1.1.20221206151952575.9000.63363.dcm`  Spot data
`RS1.2.752.243.1.1.20221205110227749.9000.25475.dcm`  Structure data

## Plan 3j `ramp_10cm`
- is a ramp across entire SOBP, starting at 100 % dose proximal edge, 0 % dose distal edge.

`RD1.2.752.243.1.1.20221206155550324.5200.68653.dcm`  Dose distribution, RayStation
`RP1.2.752.243.1.1.20221206155550324.5100.86787.dcm`  Spot data
`RS1.2.752.243.1.1.20221205110227749.9000.25475.dcm`  Structure data

## Plan 3k `ramp_4cm`
- is a special ramp:
-- in PTV it starts at 100 % dose, and being flat for 3 cm.
-- Then follows a 4 cm ramp starting at 90 % dose, stopping at 10 % dose,
-- Finally a 3 cm flat section follows at 0 % dose.

`RD1.2.752.243.1.1.20221206160246202.7300.21833.dcm`  Dose distribution, RayStation
`RP1.2.752.243.1.1.20221206160246202.7200.51467.dcm`  Spot data
`RS1.2.752.243.1.1.20221205110227749.9000.25475.dcm`  Structure data

Most likely we will proceed with ramp_4cm, and the irellevant ones will be deleted from the respository.


Corresponding easy-to-read `sobp_*.dat` files are added for each plan.
