#!/bin/bash

set -o xtrace

./get_csv.py -i data/raw/*dump
./iaa.py | tee iaa-report.txt
./get_errors.py

if [ "$1" == "deploy" ] ; then
  rsync -av --rsh=ssh --delete \
            sentences.csv \
            nodes.csv \
            error-counts.csv \
            index.html \
            show_errors.py \
            iaa-report.txt \
            thor:/disk4/html/himl/internal/ucca-eval
fi
