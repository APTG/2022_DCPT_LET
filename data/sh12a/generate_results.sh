#!/usr/bin/env bash

# function convert{
#         convertmc
# }
# set -o xtrace


# basenames for 1-d plots
bplot="NB_Z_narrow_dose NB_Z_narrow_dose_water NB_Z_narrow_LET NB_Z_narrow_LET_water NB_Z_narrow_QEFF"
# basenames for images (2-d and 1-d)
bimg="NB_XY NB_XZ ${bplot}"
# basenames for text
btxt="NB_target"

td=`pwd`           # this directory where command was started from

for dir in input/plan*
do
    echo
    ed=`ls -1 -d ${dir}/run_* | tail -1`  # extract from latest run directory only
    od=${ed}/output   # output directory
    rd=results/${dir}  # result directory

    mkdir -p ${rd}

    echo $od
    cd $od  # change into every plan*/run_*/output directory

    # generate PNG images and copy into results dir
    for b in $bimg
    do
       echo  \ \ convert "${b}*bdo" to image files
       convertmc image --many "${b}*bdo"
    done
    cd $td
    cp -v $od/NB*.png $rd

    cd $od
    # generate plotdata (.dat) and copy into results dir
    for b in $bplot
    do
            echo \ \ convert "${b}*bdo" to plotdata files
            convertmc plotdata --many "${b}*bdo"
    done
    cd $td
    cp -v $od/NB*.dat $rd

    cd $od    # generate text results for VOIs (.txt) and copy into results dir
    for b in $btxt
    do
       echo \ \ convert "${b}*bdo" to text files
       convertmc txt --many "${b}*bdo"
    done
    cd $td      # change back into ./
    cp -v $od/NB*.txt $rd

done
