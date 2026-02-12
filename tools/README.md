# Tools for repository administration

## `make_spotlists.sh`
Exports all DICOM plans to sobp.dat type files in their respective directories.
Execute this script from project directory root.
`src/make_spotlists.sh`
Needs `plan_manifest.txt` to find input plans.

## `make_mcpl.sh`
Generate MCPL files from dicom file and default beam model, use like `make_spotlists.sh`.

## `make_plandirs.sh`
Generates the directory structure for all plans. Will create any missing directories.
