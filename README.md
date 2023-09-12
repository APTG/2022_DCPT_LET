# DCPT LET-measurements 2022

All data in this repository is only preliminary, and may still be subject to change.

## Background
This repository serves as a centralized location for all Monte Carlo (MC) simulations relevant to calculating dose, LET, and other derived quantities for a proton therapy reference setup.

### Reference Setup
The primary reference setup explicitly omits detector details. This is intentional. The objective is to ascertain how effectively a detector can gauge the LET at a specific position as if the detector was absent. This concept draws parallels to cavity theory, where the dose in a given point is assessed as though no detector is present.

### Detector-Specific Calculations
Certain detectors will necessitate specialized calculations. For such cases:

- Users can fork this repository and integrate their detector-specific simulations.
- Alternatively, a dedicated folder can be introduced within this repository for those detector-specific calculations."

Multiple MC codes will be used.

We here always assume beam transport along the positive Z-axis, as is convention for most MC codes, also to minimize confusion during setup in the experimental room. z_iso = 0.0 cm marks the isocenter position.

[The DCPT beam model is supplied](https://github.com/APTG/2022_DCPT_LET/tree/main/data/resources/dcpt_beam_model), describing the proton beam starting at z_iso = -50 cm.

## Details
- Phantom geometry: [docs/phantom.md](docs/phantom.md)
- Irradiation plans and measurement positions: [docs/plans.md](https://github.com/APTG/2022_DCPT_LET/tree/main/docs/plans.md)
- Scoring geometry: [docs/scoring.md](https://github.com/APTG/2022_DCPT_LET/tree/main/docs/scoring.md)


## Contributing
You can create new issues, and create new branches based on these issues.
The branches will be reviewed before entering the master branch.


### Directory Structure
- We intend to adhere to the [Cookiecutter Data Science paradigm](https://drivendata.github.io/cookiecutter-data-science/).

- `/docs` -> general documentation in Markdown format
- `/data/resources` -> common stuff like beam model, DICOM files etc
- `/data/fluka/input`  (`topas`, `phits`) -> input files for the MC codes
- `/data/fluka/results` -> collection of results from simulation (small files!)
- `/notebooks/` - Jupyter notebooks for analysis data from individual simulations and also for comparing various codes
- `/references/` - collection of links to relevant publications, codes manuals
- `/reports/figures` - PNGs and documents with summaries/reports

### General hints:
- Any code you upload should be free of trailing whitespace.
- Use soft tabs (i.e. spaces)
