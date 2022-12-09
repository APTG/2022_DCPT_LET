#!/usr/bin/env bash

exe="cp -v"

$exe ./data/sh12a/input/plan_1a/sobp.dat ./data/resources/plans/plan1_sobp/sobp.dat
$exe ./data/sh12a/input/plan_1b/sobp.dat ./data/resources/plans/plan1_sobp/sobp.dat
$exe ./data/sh12a/input/plan_1c/sobp.dat ./data/resources/plans/plan1_sobp/sobp.dat

$exe ./data/resources/plans/plan2_160MeV/sobp.dat ./data/sh12a/input/plan_2/sobp.dat

$exe ./data/sh12a/input/plan_3i/sobp.dat ./data/resources/plans/plan3_ramped/reference/sobp_ref.dat
$exe ./data/sh12a/input/plan_3j/sobp.dat ./data/resources/plans/plan3_ramped/ramp_10cm/sobp_ramp_10cm.dat
$exe ./data/sh12a/input/plan_3k/sobp.dat ./data/resources/plans/plan3_ramped/ramp_4cm/sobp_ramp_4cm.dat
