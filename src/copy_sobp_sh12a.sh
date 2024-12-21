#!/usr/bin/env bash

exe="cp -v"

$exe ./data/resources/plans/plan01_sobp/sobp.dat ./data/sh12a/input/plan01_geoA_SOBPcent/sobp.dat
$exe ./data/resources/plans/plan01_sobp/sobp.dat ./data/sh12a/input/plan01_geoB_SOBP95/sobp.dat
$exe ./data/resources/plans/plan01_sobp/sobp.dat ./data/sh12a/input/plan01_geoC_SOBP74/sobp.dat

$exe ./data/sh12a/input/plan02_mono/sobp.dat ./data/resources/plans/plan02_geoD_mono/sobp.dat

$exe ./data/resources/plans/plan03_sobp_raystation/reference/sobp_ref.dat ./data/sh12a/input/plan03_geoA_SOBPraystation/sobp.dat
$exe ./data/resources/plans/plan04_ramp_10cm/sobp_ramp_10cm.dat ./data/sh12a/input/plan04_geoA_ramp10cm/sobp.dat
$exe ./data/resources/plans/plan05_ramp_4cm/sobp_ramp_4cm.dat ./data/sh12a/input/plan05_geoA_ramp4cm/sobp.dat
