#!/bin/bash
cd data-sync-custom
date +"%d-%m-%y-%T"
for py_file in $(find script_monthly_clean_up -name '*.py')
do
    echo $py_file
    python3 $py_file
done
