# DCPT LET-measurements 2022

All data in this repository is only preliminary, and may still be subject to change.

## Background
This repository provides access to all relevant MC simulations for calculating LET, and drived quantities.

Multiple MC codes will be used.

We here always assume beam transport along the positive z-axis, as is convention for most MC codes, also to minimize
confusion during setup in the experimental room. z_iso = 0.0 cm marks the isocenter position.

A beam model is supplied, as described for a beam starting at z_iso = -50 cm.

## Phantom design:
- 30 x 30 cm² slabs of Gammex solid water, 20 cm thick
- one 30 x 30 x 0.5 cm³ slab of PMMA which hold detectors of interest.
This slab will always be positioned so its center plane (0.25 cm depth in the PMMA slab) will mark the measurement
position.
- Target scoring volume should be small enough in z direction, and larger, but not too large latterally. We suggest:
  - 2 mm thick along z, centered on the reference depth as described below for the different plans.
  - Laterally we suggest 5 cm in x and y, centered on the z-axis.

## Plans and Measurement positions:
There will 3 plans, and in total 5 measurement points:

- **Plan 1**: SOBP covering a 10 x 10 x 10 cm³ PTV. 3 mm margin is added to the PTV.  
  The PTV is centered on z = 10.25 cm into the phantom measured from the phantom surface.
  Isocenter is always exactly at this position for Plan 1, and will not move, even if the detector plate is moved.

  Distances below in () are relative from phantom surface facing the beam, positive along beam axis.
  Distances in [] are relative to isocenter plane, or you may say, absolute positions.
  These positions are nominal, actual positions are still to be determined.
  Distances are positive downstream the beam axis, traveling along the z-axis.

    a) Center of SOBP (z_c = 10.25 cm) [z_iso = 0.0 cm]\
    b) Distal edge at 95 % dose falloff (z_d95 = 15.25 cm)  [z_iso_d95 = +5.00 cm] \
    c) Distal edge at 74 % dose falloff (z_d74 = 15.45 cm)  [z_iso_d74 = +5.20 cm]

- **Plan 2**: 160 MeV monoenergetic proton beam.\
   a) z = 2.25 cm, located on isocenter [z_iso = 0.0 cm]

- **Plan 3**: as plan 1, but ramped fields to create a local LET boost at the SOBP center.\
   a) z_c = 10.25 cm, located on isocenter [z_iso = 0.0 cm]

# Contributing

## Directory Structure
- We intend to adhere to the [Cookiecutter Data Science paradigm](https://drivendata.github.io/cookiecutter-data-science/).

From #2:
- `/data/resources` -> common stuff like beam model, DICOM files etc
- `/data/fluka/input`  (`topas`, `phits`) -> input files for the MC codes
- `/data/fluka/results` -> collection of results from simulation (small files!)
- `/notebooks/` - Jupyter notebooks for analysis data from individual simulations and also for comparing various codes
- `/references/` - collection of links to relevant publications, codes manuals
- `/reports/figures` - PNGs and documents with summaries/reports

## General hints:
- Any code you upload should be free of trailing whitespace.
- Use soft tabs (i.e. spaces)
