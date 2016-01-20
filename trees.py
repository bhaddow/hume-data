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

  # Collect text nodes
  textnodes = [] # (pos,text)
  for index,node in nodes.iterrows():
    if isinstance(node.source,str):
      textnodes.append((node.pos,node.source))
  text = pydot.Cluster(rank = 'same', rankdir='LR')
  for pos,source in sorted(textnodes, key=lambda x: int((x[0]))):
    key = source + "_" + pos
    textnode = pydot.Node(name = key, label=source)
    text.add_node(textnode)
  graph.add_subgraph(text)

  # Add the other nodes
  for index, node in nodes.iterrows():
    ucca = pydot.Node(name = node.node_id, label = node.ucca_label)
    graph.add_node(ucca)
    if isinstance(node.source,str):
      # Add link to word
      textnode = text.get_node(node.source + "_" + node.pos)
      graph.add_edge(pydot.Edge(textnode[0],ucca))
    if node.parent != "0": 
      # Link to parent
      #print("Creating {} -> {}".format(node.ucca_label, node.parent))
      graph.add_edge(pydot.Edge(ucca, node.parent))

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
