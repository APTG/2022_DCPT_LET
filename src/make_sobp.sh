#!/usr/bin/env bash

# plans list formatted like "input_directory filename_input_dicom_plan filename_output_spotlist"
plans=(
    "plan1_sobp RN.1.2.246.352.71.5.37402163639.178319.20221207095327.dcm spotlist_plan1_sobp.dat"
    "plan1_sobp_reduced RN.1.2.246.352.71.5.37402163639.178041.20221206101625.dcm spotlist_plan1_sobp_reduced_1Gy.dat"
    "plan1_sobp_reduced RN.1.2.246.352.71.5.37402163639.178042.20221206101750.dcm spotlist_plan1_sobp_reduced_0.5Gy.dat"
    "plan2_160MeV RN.1.2.246.352.71.5.37402163639.178320.20221207095327.dcm spotlist_plan2_160MeV.dat"
    "plan3_ramped/reference/ RP1.2.752.243.1.1.20221209141208883.9000.73261.dcm spotlist_plan3_sobp_ref.dat"
    "plan3_ramped/ramp_4cm/ RP1.2.752.243.1.1.20221209140939393.2000.36612.dcm plan3_sobp_ramp_4cm.dat"
    "plan3_ramped/ramp_10cm/ RP1.2.752.243.1.1.20221209141404013.2300.75558.dcm spotlist_plan3_sobp_ramp_10cm.dat"
)

exe="plan2sobp"
path_bm="data/resources/dcpt_beam_model/DCPT_beam_model__v2.csv"  # beam model to be used
dir_plan="data/resources/plans/"

plan_export() {
    set -o xtrace
    $exe -b "$path_bm" "${dir_plan}/$1/$2" "${dir_plan}/$1/$3"
    set +o xtrace
}

# Iterate over the plans array
for plan in "${plans[@]}"; do
    # Read dp, if, and of from the current plan
    read -r dp if of <<< "$plan"
    plan_export "$dp" "$if" "$of"
done
