#!/usr/bin/env python

#
# Calculate some general stats about the annotation
#

from __future__ import print_function

import argparse
import logging
import sys
import pandas

import numpy as np

from common import NODES

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-n", "--node-file", default=NODES, \
    help="CSV file containing the node data")

  args = parser.parse_args()
  allnodes = pandas.read_csv(args.node_file, converters={'node_id': str, 'parent' : str})

  #Remove nodes with no annotation
  allnodes = allnodes[allnodes.ucca_label != "M"]

  print("Node counts per annotator")
  print(allnodes['annot_id'].value_counts())

  print("Sentence counts by annotator")
  print(allnodes.groupby('annot_id').sent_id.nunique())



if __name__ == "__main__":
  main()

