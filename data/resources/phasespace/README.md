# Phase Space Files

These phase space files can serve as a particle source for various particle transport codes.

## Binary Files with Scored Particles

The following table lists the binary files containing particles scored at a plane near the particle source. Each file is 3 GB in size and contains approximately 10^8 particles. They are provided in the MCPL file format.

| Plan  | File                                                                                          |
|-------|-----------------------------------------------------------------------------------------------|
| Plan 1 | [plan01_sobp_field01.mcpl](https://s3.cloud.cyfronet.pl/2022_dcpt_let/mcpl/plan01_sobp_field01.mcpl) |  
| Plan 2 | [plan02_mono_field01.mcpl](https://s3.cloud.cyfronet.pl/2022_dcpt_let/mcpl/plan02_mono_field01.mcpl) |
| Plan 3 | [plan03_ramp_full_field01.mcpl](https://s3.cloud.cyfronet.pl/2022_dcpt_let/mcpl/plan03_ramp_full_field01.mcpl), [plan03_ramp_full_field02.mcpl](https://s3.cloud.cyfronet.pl/2022_dcpt_let/mcpl/plan03_ramp_full_field02.mcpl) |
| Plan 4 | [plan04_ramp_middle_field01.mcpl](https://s3.cloud.cyfronet.pl/2022_dcpt_let/mcpl/plan04_ramp_middle_field01.mcpl), [plan04_ramp_middle_field02.mcpl](https://s3.cloud.cyfronet.pl/2022_dcpt_let/mcpl/plan04_ramp_middle_field02.mcpl) |

## Particle Source

We used [DicomExport](https://github.com/nbassler/dicomexport) to simulate a proton beam according to the **DCPT beam model v2** and the DICOM plan files. The beam source is located at **50 cm upstream from the iso-center**. In these files, the coordinate system is defined such that **z = +50 cm** is the source plane and particles travel in the **negative z direction** towards the iso-center at z = 0. Scoring planes must be set up accordingly.

Three plans were simulated:

- `plan1`: SOBP with three PMMA plate configurations
- `plan2`: 160 MeV monoenergetic
- `plan3`: Ramped plan for LET painting
- `plan4`: Ramped plan for more agressive LET painting

In each plan, 10^8 primary particles were generated. Phasespace files holds primary protons only.
