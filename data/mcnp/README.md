# MCPN code

## Binary files with source particles

The MCNP code cannot use directly MCPL phasespace files as the source. The files needs to be converted to the SSW intermediate binary files. More on the procedere to obtain RSSA/SSW files can be found in the [MCPL hook for MCNP](https://mctools.github.io/mcpl/hooks_mcnp/).  The particle spectra in MCPL and RSSA/SSW files are the same, just stored in a different binary format.

The MCPL phase space files are described in [data/sh12a/phasespace](https://github.com/APTG/2022_DCPT_LET/tree/main/data/sh12a/phasespace)

The gzipped binary files in the RSSA/SSW file format can be downloaded from the following locations. Each of the files is 2GB in size and contains roughly 10^8 particles. The files contain the list of particles scored at a plane close to the particle source (-49.9 cm upstream from the isocenter).


### Plan1:
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan1__p1.rssa.gz
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan1__p2.rssa.gz
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan1__p3.rssa.gz


### Plan2:
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan2__p1.rssa.gz
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan2__p2.rssa.gz
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan2__p3.rssa.gz


### Plan3:
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan3__p1.rssa.gz
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan3__p2.rssa.gz
- https://s3p.cloud.cyfronet.pl/grzanka-mcpl-v1/NB_phasespace_plan3__p3.rssa.gz
