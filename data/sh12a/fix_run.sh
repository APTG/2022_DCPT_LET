#!/usr/bin/env bash
# temporary fix for lustre-symlink-fortran issue
# Enable debug mode if needed (set to 1 for more output)
DEBUG=1

echo "Searching for run.sh scripts and replacing '\$WORK_DIR' with './.'..."

# Find all run.sh scripts
find . -type f -name "run.sh" | while read -r script; do
    echo "Processing: $script"

    if [[ $DEBUG -eq 1 ]]; then
        echo "Before replacement (matching lines in $script):"
        grep '\$WORK_DIR' "$script" || echo "No matches found."
    fi

    # Replace "$WORK_DIR" with "./." only in execution lines
    sed -i 's#\$WORK_DIR#./.#g' "$script"

    if [[ $DEBUG -eq 1 ]]; then
        echo "After replacement (matching lines in $script):"
        grep './.' "$script" || echo "No matches found."
        echo "--------------------------------------------"
    fi
done

echo "All run.sh scripts processed!"
