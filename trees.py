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

COLORS = {
  "R" : "red",
  "O" : "orange", 
  "G" : "green", 
  "A" : "yellow", 
  "B" : "blue"
}

class Plotter:
  
  def __init__(self, sentences, nodes):
    self.nodes = nodes
    self.sentences = sentences

  def plot(self, sent_id, annot_id):
    """Plot an UCCA tree"""
    #print((self.nodes.columns))
    nodes = self.nodes[(self.nodes.sent_id == sent_id) & (self.nodes.annot_id == annot_id)]
    sentence = self.sentences[(self.sentences.sent_id == sent_id) & (self.sentences.annot_id == annot_id)]
    graph = pydot.Dot(graph_type='graph')

    # Target nodes
    target = pydot.Cluster("tgt", rank = 'same', rankdir='LR', color="white")
    target.add_node(pydot.Node(style="invis", name = "tgt_start"))
    target_tokens = sentence.target.iloc[0].split()
    target_tokens = target_tokens[::-1] #dot puts it backwards!
    prev_node = None
    for pos,token in enumerate(target_tokens):
      key = "tgt_" + str(len(target_tokens) - pos - 1)
      if token == ",": token = "COMMA"
      node = pydot.Node(name = key, label=token, shape="rectangle")
      target.add_node(node)
      #if prev_node:
      #  target.add_edge(pydot.Edge(prev_node,node))
      prev_node = node
    target.add_node(pydot.Node(style="invis", name = "tgt_end"))
    graph.add_subgraph(target)

    # Collect source text nodes
    textnodes = [] # (pos,text)
    src_keys = set()
    for index,node in nodes.iterrows():
      if isinstance(node.source,str):
        textnodes.append((node.pos,node.source))
    text = pydot.Cluster("src", rank = 'same', rankdir='LR', color="white")
    text.add_node(pydot.Node(style="invis", name = "src_start"))
    for pos,source in sorted(textnodes, key=lambda x: int((x[0]))):
      key = "src_" + pos
      src_keys.add(key)
      textnode = pydot.Node(name = key, label=source, shape="rectangle")
      text.add_node(textnode)
    text.add_node(pydot.Node(style="invis", name = "src_end"))
    graph.add_subgraph(text)

    graph.add_edge(pydot.Edge("tgt_start", "src_start", style="invis"))
    graph.add_edge(pydot.Edge("tgt_end", "src_end", style="invis"))

    # Alignment
    print (sentence['source'].iloc[0])
    print (sentence['target'].iloc[0])
    print (sentence['align'].iloc[0])
    for align in sentence['align'].iloc[0].split():
      src_pos,tgt_pos = align.split("-")
      src_key = "src_" + str(src_pos)
      if src_key in src_keys:
        # Alignment nodes should not affect positioning, so constraint=false
        graph.add_edge(pydot.Edge(src_key,  "tgt_" + str(tgt_pos), constraint=False))

    # Add the other nodes
    for index, node in nodes.iterrows():
      ucca = pydot.Node(name = node.node_id, label = node.ucca_label,
         fillcolor = COLORS[node.mt_label], style="filled", shape="circle")
      graph.add_node(ucca)
      if isinstance(node.source,str):
        # Add link to word
        textnode = text.get_node("src_" + node.pos)
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

  nodes = pandas.read_csv("nodes.csv", converters={'node_id': str, 'parent' : str})
  sentences = pandas.read_csv("sentences.csv")
  plotter = Plotter(sentences, nodes)
  
  annot = "ro1"
  sent = 505
  graph = plotter.plot(sent,annot)
  graph.write_png("tree.png")


if __name__ == "__main__":
  main()
