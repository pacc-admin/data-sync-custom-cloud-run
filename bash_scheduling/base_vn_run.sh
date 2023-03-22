#!/bin/bash
cd data-sync-custom
date +"%d-%m-%y-%T"
for py_file in $(find script_base_vn* -name '*.py')
do
    echo '*******' 'Start' $py_file '*******'
    RESULT=$(python3 $py_file)
    echo $RESULT
    if [[ $RESULT =~ "Fail" ]] 
    then
        echo "Error"
        exit 1
    else
        exit 0
    fi
    echo '*******' 'End' $py_file '*******'
done
