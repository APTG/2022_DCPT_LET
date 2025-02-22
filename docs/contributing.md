# Contributing

Genereal guidelines for contributing to this project.
Contact @nbassler or @grzanka if you wish to commit to branches.

### Directory Structure
- We intend to adhere to the [Cookiecutter Data Science paradigm](https://drivendata.github.io/cookiecutter-data-science/).

- `/docs` -> general documentation in Markdown format
- `/data/resources` -> common stuff like beam model, DICOM files etc
- `/data/fluka/input`  (`topas`, `phits`) -> input files for the MC codes
- `/data/fluka/results` -> collection of results from simulation (small files!)
- `/notebooks/` - Jupyter notebooks for analysis data from individual simulations and also for comparing various codes
- `/references/` - collection of links to relevant publications, codes manuals
- `/reports/figures` - PNGs and documents with summaries/reports
- `/src` - scripts for post-process intercomparisons

### General hints:
- Any code you upload should be free of trailing whitespace.
- Use soft tabs (i.e. spaces)
- For python code, use flake8/pep8 before comitting.
