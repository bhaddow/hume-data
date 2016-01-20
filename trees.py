#!/usr/bin/env python
from __future__ import print_function

#
# Draws the UCCA trees, with annotations
#
import argparse
import logging
import math
import pandas
import pydot
import sys

#TODO: Use Cluster and randir=LR for ordering

def plot(nodes):
  """Plot an UCCA tree"""
  graph = pydot.Dot(graph_type='graph')
  text = pydot.Subgraph(rank = 'same')
  for index,node in nodes.iterrows():
    if isinstance(node.source, str):
      textnode = pydot.Node(node.source)
      text.add_node(textnode)
      graph.add_edge(pydot.Edge(node.node_id, textnode))
    if node.parent == "0": continue
    edge = pydot.Edge(node.node_id, node.parent)
    graph.add_edge(edge)
  graph.add_subgraph(text)
  return graph
    
def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  args = parser.parse_args()

  alldata = pandas.read_csv("nodes.csv", converters={'node_id': str, 'parent' : str})
  
  annot = "cs1"
  sent = 505
  lang = "cs"
  selected = alldata[(alldata['annot_id']==annot) & (alldata['sent_id'] == sent) & (alldata['lang'] == lang)]
  graph = plot(selected)
  graph.write_png("tree.png")


if __name__ == "__main__":
  main()
