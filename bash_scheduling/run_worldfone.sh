#!/bin/bash
cd data-sync-custom
git pull origin main
/usr/bin/python3 /home/pacc_workplace/data-sync-custom/script_worldfone/cdrs_historical.py