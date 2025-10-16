#!/bin/bash
# Change working directory to the repository root (parent of this script's folder)
cd "$(dirname "$0")/.." || exit 1
date +"%d-%m-%y-%T"
for py_file in $(find script_base_vn* -name '*.py')
do
    echo '*******' 'Start' $py_file '*******'
    python3 $py_file || exit 1
    echo '*******' 'End' $py_file '*******'
done
