# Phase Space Files

These phase space files can serve as a particle source for various particle transport codes.

## Binary Files with Scored Particles

The following binary files contain lists of particles scored at a plane near the particle source. Each file is 3 GB in size and contains approximately 10^8 particles.

They are provided in the MCPL file format and can be downloaded here:

### Plan 1
- [NB_phasespace_plan1__p1.mcpl](https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan1__p1.mcpl)

### Plan 2
- [NB_phasespace_plan2__p1.mcpl](https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan2__p1.mcpl)

### Plan 3
- [NB_phasespace_plan3__p1.mcpl](https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan3__p1.mcpl)

## Particle Source

In these Monte Carlo (MC) simulations, we commonly use a particle source that emits particles from the plane at **Z = -50 cm**, directed roughly toward the positive Z-axis. We use this coordinate system convention even though it is not consistent with the Treatment Planning System (TPS) settings.

We used **SHIELD-HIT12A** to simulate a proton beam according to the **DCPT beam model** and the DICOM plan files, with the beam source located at **Z = -50 cm**.

Three plans were simulated:

- `plan1`: SOBP with three PMMA plate configurations  
- `plan2`: 160 MeV monoenergetic  
- `plan3`: Ramped plans for LET painting  

In each plan, 10^8 primary particles were generated.

The input files used to generate the phase space files are located in [data/sh12a/phasespace](https://github.com/APTG/2022_DCPT_LET/tree/main/data/sh12a/phasespace).

## Scoring Plane

After traveling **1 mm** of air, the beam hit the scoring plane positioned at **Z = -49.9 cm**. This 1 mm of air was used to avoid numerical issues associated with scoring particles exactly at their generation point.

Each phase space file contains only primary protons (exactly 10^8 particles per file).
