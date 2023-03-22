#!/bin/bash
cd data-sync-custom
date +"%d-%m-%y-%T"
for py_file in $(find script_base_vn* -name '*.py')
do
    echo '*******' 'Start' $py_file '*******'
    python3 $py_file
    echo '*******' 'End' $py_file '*******'
done
