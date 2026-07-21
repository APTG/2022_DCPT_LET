# FLUKA.cern input files

This folder contains FLUKA input cards for the LET benchmark cases.

Each case folder contains:

- `<case>.inp`: FLUKA input card for the individual benchmark case.
- `sobp.dat`: spot/SOBP source file read by the custom FLUKA source routine.

The input cards use a custom FLUKA executable. The relevant user routines are maintained in `au-fluka-tools`, in particular:

- `fluka_sobp_source/`: source sampler for the SOBP/spot files.
- `fluka_let_scoring/`: FLUKA LET scoring routine used for LET moment scoring.

Compiled FLUKA executables, temporary run directories, random seed files, logs, errors, and binary output files are not stored in this input directory.
