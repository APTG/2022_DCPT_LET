# PHITS code

## Binary files with source particles

The PHITS code cannot use directly MCPL phasespace files as the source. The MCPL phaspace files needs to be converted to the so called "PHITS dump binary files". More on the procedere to obtain dump files can be found in the [MCPL hook for PHITS](https://mctools.github.io/mcpl/hooks_phits/).  The particle spectra in MCPL and dump files are the same, just stored in a different binary format.

The MCPL phase space files are described in [data/sh12a/phasespace](https://github.com/APTG/2022_DCPT_LET/tree/main/data/resources/phasespace)

The binary files in the PHITS dump file format can be downloaded from the following locations. Each of the files is ~8GB in size and contains roughly 10^8 particles. The files contain the list of particles scored at a plane close to the particle source (-49.9 cm upstream from the isocenter).


### Plan1:
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan1__p1.dmp
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan1__p2.dmp
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan1__p3.dmp


### Plan2:
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan2__p1.dmp
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan2__p2.dmp
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan2__p3.dmp


### Plan3:
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan3__p1.dmp
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan3__p2.dmp
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan3__p3.dmp
