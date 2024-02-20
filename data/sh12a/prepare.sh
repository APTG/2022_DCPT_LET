#!/usr/bin/env bash

# copies all spotlists from resources into input directories

# for SH12A normal calculations
cp -v ../resources/plans/plan1_sobp/spotlist_plan1_sobp.dat input/plan_1a/spotlist.dat
cp -v ../resources/plans/plan1_sobp/spotlist_plan1_sobp.dat input/plan_1b/spotlist.dat
cp -v ../resources/plans/plan1_sobp/spotlist_plan1_sobp.dat input/plan_1c/spotlist.dat

cp -v ../resources/plans/plan1_sobp_reduced/spotlist_plan1_sobp_reduced_1Gy.dat input/plan_1a_reduced/spotlist.dat
cp -v ../resources/plans/plan1_sobp_reduced/spotlist_plan1_sobp_reduced_1Gy.dat input/plan_1b_reduced/spotlist.dat
cp -v ../resources/plans/plan1_sobp_reduced/spotlist_plan1_sobp_reduced_1Gy.dat input/plan_1c_reduced/spotlist.dat

cp -v ../resources/plans/plan2_160MeV/spotlist_plan2_160MeV.dat input/plan_2/spotlist.dat

cp -v ../resources/plans/plan3_ramped/reference/spotlist_plan3_sobp_ref.dat input/plan_3i/spotlist.dat
cp -v ../resources/plans/plan3_ramped/ramp_10cm/spotlist_plan3_sobp_ramp_10cm.dat input/plan_3j/spotlist.dat
cp -v ../resources/plans/plan3_ramped/ramp_4cm/spotlist_plan3_sobp_ramp_4cm.dat input/plan_3k/spotlist.dat


# for SH12A phasespace
cp -v ../resources/plans/plan1_sobp/spotlist_plan1_sobp.dat phasespace/plan1.dat
cp -v ../resources/plans/plan1_sobp_reduced/spotlist_plan1_sobp_reduced_1Gy.dat phasespace/plan1r.dat

cp -v ../resources/plans/plan2_160MeV/spotlist_plan2_160MeV.dat phasespace/plan2.dat

cp -v ../resources/plans/plan3_ramped/reference/spotlist_plan3_sobp_ref.dat phasespace/plan3i.dat
cp -v ../resources/plans/plan3_ramped/ramp_10cm/spotlist_plan3_sobp_ramp_10cm.dat phasespace/plan3j.dat
cp -v ../resources/plans/plan3_ramped/ramp_4cm/spotlist_plan3_sobp_ramp_4cm.dat phasespace/plan3k.dat

