#!/bin/bash

set -o xtrace

./get_csv.py -i data/raw/*dump
./iaa.py | tee iaa-report.txt
#./get_trees.py
