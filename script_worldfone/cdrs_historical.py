#!/usr/bin/env python3
import sys
import os

# Ensure dbconnector is on path when running from repo root or elsewhere
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import worldfone


def main():
	schema = 'WORLDFONE'
	table_id = 'cdrs'

	# Run the historical loader
	worldfone.worldfone_bq_historical_v2(schema, table_id)


if __name__ == "__main__":
	main()