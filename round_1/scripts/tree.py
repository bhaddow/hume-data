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

from common import NODES, SENTENCES

COLORS = {
  "R" : "red",
  "O" : "orange", 
  "G" : "green", 
  "A" : "yellow", 
  "B" : "blue",
  "M" : "white"
}

LOG = logging.getLogger(__name__)

class Plotter:
  
  def __init__(self, sentences, nodes):
    self.nodes = nodes
    self.sentences = sentences
  
  def make_label(self,label):
    #escape quotes
    label = label.replace("\"", "\\\"")
    # enclose in quotes
    label = "\"{}\"".format(label)
    return label

  def plot_tree(self, sent_id, annot_id):
    """Plot an UCCA tree, with source and target sentences"""
    #print((self.nodes.columns))
    nodes = self.nodes[(self.nodes.sent_id == sent_id) & (self.nodes.annot_id == annot_id)]
    sentence = self.sentences[(self.sentences.sent_id == sent_id) & (self.sentences.annot_id == annot_id)]
    graph = pydot.Dot(graph_type='graph', splines=False, rankdir="TB")

    source,target = self.plot_source_target(graph,sentence,nodes)

    # Add the ucca tree
    for index, node in nodes.iterrows():
      ucca = pydot.Node(name = node.node_id, label = node.ucca_label,
         fillcolor = COLORS[node.mt_label], style="filled", shape="circle")
      graph.add_node(ucca)
      if isinstance(node.source,str):
        # Add link to word
        textnode = source.get_node("src_" + node.pos.split()[0])
        graph.add_edge(pydot.Edge(textnode[0],ucca))
      if node.parent != "0": 
        # Link to parent
        #print("Creating {} -> {}".format(node.ucca_label, node.parent))
        graph.add_edge(pydot.Edge(ucca, node.parent))
    return graph

  def make_split_label(self,ucca_label, mt_label1, mt_label2):
      return """<
      <table cellpadding="0" cellborder="0" cellspacing="0" border="1">
      <tr>
      <td bgcolor=\"{1}\">{0}&nbsp;</td>
      <td bgcolor=\"{2}\"><font color=\"{2}\">{0}&nbsp;</font></td>
      </tr>
      </table>
      >""".format(ucca_label, COLORS[mt_label1], COLORS[mt_label2])


  def plot_doubly_annotated_tree(self, sent_id, annot_id1, annot_id2):
    """Plot a doubly annotated UCCA tree with its source and target sentences."""
    nodes1 = self.nodes[(self.nodes.sent_id == sent_id) & (self.nodes.annot_id == annot_id1)]
    sentence1 = self.sentences[(self.sentences.sent_id == sent_id) & (self.sentences.annot_id == annot_id1)]
    graph = pydot.Dot(graph_type='graph', splines=False, rankdir="TB")

    source,target = self.plot_source_target(graph,sentence1,nodes1)
    # Merge the annotations
    nodes2 = self.nodes[(self.nodes.sent_id == sent_id) & (self.nodes.annot_id == annot_id2)]
    merged = nodes1.merge(nodes2, on="node_id")

    # Add the ucca tree
    for index, node in merged.iterrows():
      ucca = pydot.Node(name = node.node_id, margin=0, height=0.2, width=0.45, penwidth=0, 
         label  =  self.make_split_label(node.ucca_label_x,node.mt_label_x,node.mt_label_y), style="filled", shape="rectangle")
      graph.add_node(ucca)
      if isinstance(node.source_x,str):
        # Add link to word
        textnode = source.get_node("src_" + node.pos_x.split()[0])
        graph.add_edge(pydot.Edge(textnode[0],ucca))
      if node.parent_x != "0": 
        # Link to parent
        #print("Creating {} -> {}".format(node.ucca_label, node.parent))
        graph.add_edge(pydot.Edge(ucca, node.parent_x))
    return graph

  def plot_source_target(self,graph,sentence,nodes):
    # Source nodes
    textnodes = [] # (pos,text)
    src_keys = set()
    for index,node in nodes.iterrows():
      if isinstance(node.source,str):
        textnodes.append((node.pos.split()[0],node.source))
    source_graph = pydot.Cluster("src", rank = 'same', rankdir='LR', color="white")
    source_graph.add_node(pydot.Node(style="invis", name = "src_start"))
    for pos,source in sorted(textnodes, key=lambda x: int((x[0])) ):
      key = "src_" + pos
      src_keys.add(key)
      textnode = pydot.Node(name = key, label=self.make_label(source), shape="rectangle")
      source_graph.add_node(textnode)
    source_graph.add_node(pydot.Node(style="invis", name = "src_end"))
    graph.add_subgraph(source_graph)

    # Target nodes
    target_graph = pydot.Cluster("tgt", rank = 'same', rankdir='LR', color="white")
    target_graph.add_node(pydot.Node(style="invis", name = "tgt_start"))
    target_tokens = sentence.target.iloc[0].split()
    target_tokens = target_tokens[::-1] #dot puts it backwards!
    prev_node = None
    for pos,token in enumerate(target_tokens):
      key = "tgt_" + str(len(target_tokens) - pos - 1)
      node = pydot.Node(name = key, label=self.make_label(token), shape="rectangle")
      target_graph.add_node(node)
      #if prev_node:
      #  target.add_edge(pydot.Edge(prev_node,node, style="invis"))
      prev_node = node
    target_graph.add_node(pydot.Node(style="invis", name = "tgt_end"))
    graph.add_subgraph(target_graph)

    graph.add_edge(pydot.Edge("tgt_start", "src_start", style="invis"))
    graph.add_edge(pydot.Edge("tgt_end", "src_end", style="invis"))

    # Alignment
    LOG.debug(sentence['source'].iloc[0])
    LOG.debug(sentence['target'].iloc[0])
    LOG.debug(sentence['align'].iloc[0])
    for align in sentence['align'].iloc[0].split():
      src_pos,tgt_pos = align.split("-")
      src_key = "src_" + str(src_pos)
      if src_key in src_keys:
        # Alignment nodes should not affect positioning, so constraint=false
        graph.add_edge(pydot.Edge(src_key,  "tgt_" + str(tgt_pos), constraint=False, headport="s", tailport="n"))

    return source_graph,target_graph
 
def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  parser.add_argument("-a", "--annotator-id")
  parser.add_argument("-l", "--language")
  parser.add_argument("-s", "--sentence-id", type=int, default=169)
  args = parser.parse_args()

  nodes = pandas.read_csv(NODES, converters={'node_id': str, 'parent' : str})
  sentences = pandas.read_csv(SENTENCES)
  plotter = Plotter(sentences, nodes)

  if args.annotator_id:
    graph = plotter.plot_tree(args.sentence_id,args.annotator_id)
  elif args.language:
    # Find the annotators
    annotators = nodes[(nodes['lang'] == args.language) & (nodes['sent_id'] == args.sentence_id)]['annot_id'].unique()
    if len(annotators) == 1:
      graph = plotter.plot_tree(args.sentence_id,annotators[0])
    elif len(annotators) == 2:
      annotators.sort()
      graph = plotter.plot_doubly_annotated_tree(args.sentence_id, *annotators)
    else:
      raise RuntimeError("Need exactly 1 or 2 anotations for sentence id {}. Found {}".format(args.sentence_id, len(annotators)))
  else:
    raise RuntimeError("Need to specify annotator ID or language")
  graph.write_png("tree.png")


if __name__ == "__main__":
  main()
