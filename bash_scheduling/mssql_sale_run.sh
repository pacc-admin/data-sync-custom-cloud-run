#!/bin/bash
cd data-sync-custom
date +"%d-%m-%y-%T"
for py_file in $(find script_mssql_sale -name '*.py')
do
    echo $py_file
    python3 $py_file || exit 1
done
