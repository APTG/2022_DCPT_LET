#!/usr/bin/env bash

exe="plan2sobp"
path_bm="data/resources/dcpt_beam_model/DCPT_beam_model__v2.csv"
dir_plan="data/resources/plans/"

plan_export() {
    set -o xtrace
    $exe -b $path_bm ${dir_plan}/${dp}/${if} ${dir_plan}/${dp}/${of}
    set +o xtrace
}



dp=plan1_sobp if=RN.1.2.246.352.71.5.37402163639.178319.20221207095327.dcm of=sobp.dat
plan_export
dp=plan2_160MeV if=RN.1.2.246.352.71.5.37402163639.178320.20221207095327.dcm of=sobp.dat
plan_export
dp=plan3_ramped/reference/ if=RP1.2.752.243.1.1.20221206151952575.9000.63363.dcm of=sobp_ref.dat
plan_export
dp=plan3_ramped/ramp_10cm/ if=RP1.2.752.243.1.1.20221206155550324.5100.86787.dcm of=sobp_ramp_10cm.dat
plan_export
dp=plan3_ramped/ramp_4cm/ if=RP1.2.752.243.1.1.20221206160246202.7200.51467.dcm of=sobp_ramp_4cm.dat
plan_export
