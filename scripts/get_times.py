#!/usr/bin/env python
from __future__ import print_function


#
# Collects time stamps and intervals
#

import argparse
import logging
import math
import os
import os.path
import pandas
import sys

import matplotlib.pyplot as plt
import numpy as np

from scipy import stats

from common import SENTENCES

LOG = logging.getLogger(__name__)
   
def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--sentences-file", default=SENTENCES)
  args = parser.parse_args()

  sentences = pandas.read_csv(args.sentences_file, converters={'timestamp' : pandas.to_datetime})
  sentences.sort_values(by = 'timestamp',inplace=True )

  annots = ("de1","cs1", "ro1", "pl1",  "de2", "ro2", "pl2")
  fig, axes = plt.subplots(nrows=len(annots), ncols=1, figsize=(12,12))
  fig.tight_layout()
  for fig_id, annot_id in enumerate(annots):
    by_annot = sentences[sentences.annot_id == annot_id]
    diffs = by_annot.timestamp - by_annot.timestamp.shift()
    diffs = diffs.dt.seconds
    diffs = diffs.dropna()
    #print (diffs.head())
    bins = diffs.groupby(pandas.cut(diffs,np.arange(0,3600,20))).size()
    #print("mode", bins.idxmax(), bins.max())
    diffs = diffs[diffs < 3600]
    ax = plt.subplot(len(annots),1,fig_id)
    ax.set_title("Timestamp delta histogram for {}".format(annot_id))
    diffs.hist(ax = ax, bins=180)
    median = np.median(diffs[diffs < 500])
    plt.axvline(median, color='r', linestyle='dashed')
    print("Annot: {} Median: {}".format(annot_id,median))
  graph_file_name = "times.png"
  plt.savefig(graph_file_name)

if __name__ == "__main__":
  main()

