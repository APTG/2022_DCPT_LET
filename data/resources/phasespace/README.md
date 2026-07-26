# Phase Space Files

These phase space files can serve as a particle source for various particle transport codes.

## Binary Files with Scored Particles

The following table lists the binary files containing particles scored at a plane near the particle source. Each file is 3 GB in size and contains approximately 10^8 particles. They are provided in the MCPL file format.

| Plan  | File                                                                                          |
|-------|-----------------------------------------------------------------------------------------------|
| Plan 1 | [plan01_sobp_field01.mcpl](https://s3p.cloud.cyfronet.pl/2022dcptlet/mcpl/plan01_sobp_field01.mcpl) |  
| Plan 2 | [plan02_mono_field01.mcpl](https://s3p.cloud.cyfronet.pl/2022dcptlet/mcpl/plan02_mono_field01.mcpl) |
| Plan 3 | [plan03_ramp_full_field01.mcpl](https://s3p.cloud.cyfronet.pl/2022dcptlet/mcpl/plan03_ramp_full_field01.mcpl), [plan03_ramp_full_field02.mcpl](https://s3p.cloud.cyfronet.pl/2022dcptlet/mcpl/plan03_ramp_full_field02.mcpl) |
| Plan 4 | [plan04_ramp_middle_field01.mcpl](https://s3p.cloud.cyfronet.pl/2022dcptlet/mcpl/plan04_ramp_middle_field01.mcpl), [plan04_ramp_middle_field02.mcpl](https://s3p.cloud.cyfronet.pl/2022dcptlet/mcpl/plan04_ramp_middle_field02.mcpl) |

## Particle Source

We used [DicomExport](https://github.com/nbassler/dicomexport) to simulate a proton beam according to the DCPT beam model and the DICOM plan files. The MCPL files are written in IEC 61217 coordinates, which is the standard coordinate convention for treatment gantries. In this convention the gantry beam source is upstream at positive z, so particles travel in the **−z direction** toward the iso-center at z = 0.

The beam source plane is located upstream from the iso-center. Its distance depends on the beam model: **50 cm for DCPT beam model v2** and **60 cm for DCPT beam model v5**; see the [beam-model README](../dcpt_beam_model/README.md).

In these files the source plane is therefore at `z = +50 cm` for v2 or `z = +60 cm` for v5. This is the *MCPL phase-space frame*: note it is the mirror image (travel −z) of the native MC scoring frame used elsewhere in this repo (source at negative z, travel +z). If a transport code requires particles travelling in the positive z direction, do not only flip the sign of z. Apply a proper 180 degree rotation around x or y, which also flips the corresponding transverse axis. "Upstream" always means the source side, independent of the sign convention. Scoring planes must be set up accordingly. See [docs/coordinates.md](../../../docs/coordinates.md) for the full frame contract.

Three plans were simulated:

- `plan1`: SOBP with three PMMA plate configurations
- `plan2`: 160 MeV monoenergetic
- `plan3`: Ramped plan for LET painting
- `plan4`: Ramped plan for more agressive LET painting

In each plan, 10^8 primary particles were generated. Phasespace files holds primary protons only.
