# Description of scripts

## fetch_results_from_zenodo.py
Downloads all results from Zenodo and extracts them to the results directory.
Execute this script from project directory root:
`python3 src/fetch_results_from_zenodo.py`

## `make_sobp.sh`
Exports all DICOM plans to sobp.dat type files in their respective directories.
Execute this script from project directory root.
`src/make_sobp.sh`


## `copy_sobp_sh12a.sh`
Copies all plan sobp.dat type files to the respective SH12A input file directories.
Execute this script from project directory root.
`src/copy_sobp_sh12a.sh`
