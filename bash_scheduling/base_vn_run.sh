#!/bin/bash
cd pacc-data-sync-custom
date +"%d-%m-%y-%T"
for py_file in $(find script_base_vn* -name '*.py')
do
    echo $py_file
    #python3 $py_file
done
