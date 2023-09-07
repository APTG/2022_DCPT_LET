# Guidelines for contributing

This directory contains:
 - common [resources](https://github.com/APTG/2022_DCPT_LET/tree/main/data) like beam model, treatment plan DICOM files, phase space files etc
 - input files and results obtained using various MC codes: [SHIELD-HIT12A](https://github.com/APTG/2022_DCPT_LET/tree/main/data/sh12a), [TOPAS](https://github.com/APTG/2022_DCPT_LET/tree/main/data/topas)

## Coordindate system

In this project we assume that irrespectively of the gantry and couch angle, then beam is always directed along the positive Z axis. When necessary the phantom volume needs to be rotated to match this convention.

In order to compare the results with TPS or other sources we can transform the MC results to desired coordinate system.

