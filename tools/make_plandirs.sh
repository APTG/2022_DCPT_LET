#!/usr/bin/env bash

DIRS=(
plan01_field01_geoA_SOBPcent
plan01_field01_geoB_SOBP95
plan01_field01_geoC_SOBP74
plan02_field01_geoD_mono
plan03_field01_geoA_rampFull
plan03_field02_geoA_rampFull
plan04_field01_geoA_rampMiddle
plan04_field02_geoA_rampMiddle
)

CREATE_TODO=false

# Parse options
while getopts "t" opt; do
    case $opt in
        t)
            CREATE_TODO=true
            ;;
        *)
            echo "Usage: $0 [-t] [base_dir]"
            exit 1
            ;;
    esac
done

shift $((OPTIND - 1))

# Set the base directory to the first argument or default to the current directory
BASE_DIR=${1:-.}

for dir in "${DIRS[@]}"
do
    mkdir -p "$BASE_DIR/$dir"
    if [ "$CREATE_TODO" = true ]; then
        touch "$BASE_DIR/$dir/TODO"
    fi
done