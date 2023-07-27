# The phase space files

Phase space files which may serve as a source of particles for the various particle transport codes.

## Binary files with scored particles

Following binary files contain the list of particles scored at a plane close to the particle source. Each of the files is 3GB in size and contains roughly 10^8 particles.

The binary files in the MCPL file format can be downloaded from the following locations:

### Plan1:
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan1__p1.mcpl
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan1__p2.mcpl
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan1__p3.mcpl


### Plan2:
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan2__p1.mcpl
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan2__p2.mcpl
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan2__p3.mcpl


### Plan3:
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan3__p1.mcpl
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan3__p2.mcpl
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan3__p3.mcpl



## Particle source

In the MC simulations we commonly use particle source which emits the simulation from the plane at Z = -50cm. The particles are emitted roughly towards positive Z axis. This convention of coordindate system is used, despite not being consistent with the TPS settings.

We used SHIELD-HIT12A to simulate a proton beam according to the DCPT beam model and the DICOM plan files. The beam source was located at Z=-50cm. 

Three plans were simulated:
- `plan1` SOBP for the three PMMA plate configurations.
- `plan2` 160 MeV mono-energetic
- `plan3` ramped plans for LET-painting.

In each plan 10^8 primary particles were generated. 

The input files used to generate the phase space files are in [data/sh12a/phasespace](https://github.com/APTG/2022_DCPT_LET/tree/main/data/sh12a/phasespace)

## Scoring plane

After travelling 1mm of air the beam was hitting the scoring plane positioned at Z=-49.9cm. The 1mm of air was used to avoid any numerical issues in scoring the particles exactly at the place they were generated.

Three different filters were used in scoring the particles:
- `p1` - primary protons (exactly 10^8 particles per file)
- `p2` - primary and secondary protons (slightly more than 10^8 particles per file)
- `p3` - no filter, this file includes protons, neutrons and other charged particles

For most of the use cases `p1` filter should be enough. We decided to provide also `p2` and `p3` filters for the sake of completeness and to test the capabilities of the binary file format to record possible particle types.

Scoring with `p2` adds a negligible amount of secondary protons generated in the nuclear reactions in the thin layer of 1mm of air. Scoring with `p3` adds also neutrons and other charged particles.

