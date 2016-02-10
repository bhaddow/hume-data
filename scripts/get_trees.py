#!/usr/bin/env python
from __future__ import print_function


#
# Draws all the annotated UCCA trees
#

import argparse
import logging
import math
import os
import os.path
import pandas
import pydot
import sys

from tree import Plotter

LOG = logging.getLogger(__name__)
   
def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
  parser = argparse.ArgumentParser()
  parser.add_argument("-n", "--nodes-file", default="nodes.csv")
  parser.add_argument("-s", "--sentences-file", default="sentences.csv")
  parser.add_argument("-o", "--output-dir", default="trees")
  args = parser.parse_args()

  nodes = pandas.read_csv(args.nodes_file, converters={'node_id': str, 'parent' : str})
  sentences = pandas.read_csv(args.sentences_file)
  plotter = Plotter(sentences, nodes)

  if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)
  LOG.info("Writing trees to directory: {}/".format(args.output_dir))

  #NOTE: Iterating through rows like this is not really the pandas way
  for i,row in enumerate(sentences.iterrows()):
    sent_id,annot_id = row[1].sent_id,row[1].annot_id
    LOG.debug("Plotting sentence id: {} annotator id: {}".format(sent_id,annot_id))
    graph_file = "{}/tree_{}_{}.png".format(args.output_dir,sent_id,annot_id)
    graph = plotter.plot_tree(sent_id,annot_id)
    graph.write_png(graph_file)
    if i  and i % 50 == 0:
      LOG.info("Processed {} trees".format(i))

if __name__ == "__main__":
  main()


