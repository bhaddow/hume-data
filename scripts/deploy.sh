#!/bin/bash

set -o xtrace

rsync -av --rsh=ssh --delete \
          sentences.csv \
          nodes.csv \
          index.html \
          show_errors.py \
          show_trees.py \
          show_tree.py \
          show_iaa_rg.py \
          iaa-report.txt \
          trees \
          thor:/disk4/html/himl/internal/ucca-eval
