#!/usr/bin/env bash

# copy all current spotlists

cp -v  ../resources/plans/plan1_sobp/spotlist_plan1_sobp.dat input/plan_1a/spotlist.dat
cp -v  ../resources/plans/plan1_sobp/spotlist_plan1_sobp.dat input/plan_1b/spotlist.dat
cp -v  ../resources/plans/plan1_sobp/spotlist_plan1_sobp.dat input/plan_1c/spotlist.dat

cp -v  ../resources/plans/plan1_sobp_reduced/spotlist_plan1_sobp_reduced_1Gy.dat input/plan_1a_reduced/spotlist.dat
cp -v  ../resources/plans/plan1_sobp_reduced/spotlist_plan1_sobp_reduced_1Gy.dat input/plan_1b_reduced/spotlist.dat
cp -v  ../resources/plans/plan1_sobp_reduced/spotlist_plan1_sobp_reduced_1Gy.dat input/plan_1c_reduced/spotlist.dat

cp -v  ../resources/plans/plan2_160MeV/spotlist_plan2_160MeV.dat input/plan_2/spotlist.dat

cp -v  ../resources/plans/plan3_ramped/reference/spotlist_plan3_sobp_ref.dat input/plan_3i/spotlist.dat
cp -v  ../resources/plans/plan3_ramped/ramp_10cm/spotlist_plan3_sobp_ramp_10cm.dat input/plan_3j/spotlist.dat
cp -v ../resources/plans/plan3_ramped/ramp_4cm/spotlist_plan3_sobp_ramp_4cm.dat input/plan_3k/spotlist.dat
