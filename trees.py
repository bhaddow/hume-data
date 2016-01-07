#!/usr/bin/env python
from __future__ import print_function

#
# Draws the UCCA trees, with annotations
#
import argparse
import logging
import pandas
import pydot
import sys


def plot(nodes):
  """Plot an UCCA tree"""
  graph = pydot.Dot(graph_type='graph')
  for index,node in nodes.iterrows():
    if node.parent == "0": continue
    edge = pydot.Edge(node.id, node.parent)
    graph.add_edge(edge)
  return graph
    
def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  args = parser.parse_args()

  alldata = pandas.read_csv("data.csv", converters={'id': str, 'parent' : str})
  
  annot = "cs1"
  sent = 505
  lang = "cs"
  selected = alldata[(alldata['user']==annot) & (alldata['sent'] == sent) & (alldata['lang'] == lang)]
  graph = plot(selected)
  graph.write_png("tree.png")


if __name__ == "__main__":
  main()
