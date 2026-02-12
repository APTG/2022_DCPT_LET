# Phase Space Files

These phase space files can serve as a particle source for various particle transport codes.

## Binary Files with Scored Particles

The following table lists the binary files containing particles scored at a plane near the particle source. Each file is 3 GB in size and contains approximately 10^8 particles. They are provided in the MCPL file format.

| Plan  | File                                                                                          |
|-------|-----------------------------------------------------------------------------------------------|
| Plan 1 | [plan01_sobp_field01.mcpl](https://) |  TODO: Leszek
| Plan 2 | [plan02_mono_field01.mcpl](https://) |
| Plan 3 | [plan03_ramp_full_field01.mcpl](https://) | [plan03_ramp_full_field02.mcpl](https://) |
| Plan 4 | [plan04_ramp_middle_field01.mcpl](https://) | [plan04_ramp_middle_field02.mcpl](https://) |

## Particle Source

In these Monte Carlo (MC) simulations, we commonly use a particle source that emits particles from the plane at **Z = +50 cm**, directed traveling along Z-axis in negative direction. We use this coordinate to be consistent with the Treatment Planning System (TPS) settings.

We used [DicomExport](https://github.com/nbassler/dicomexport) to simulate a proton beam according to the **DCPT beam model** and the DICOM plan files, with the beam source located at **Z = -50 cm**.

Three plans were simulated:

- `plan1`: SOBP with three PMMA plate configurations
- `plan2`: 160 MeV monoenergetic
- `plan3`: Ramped plan for LET painting
- `plan4`: Ramped plan for more agressive LET painting

In each plan, 10^8 primary particles were generated. Phasespace files holds primary protons only.
