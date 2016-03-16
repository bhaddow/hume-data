#!/usr/bin/env python
from __future__ import print_function

import argparse
import logging
import sys
import pandas

import numpy as np
from  pandas_confusion import ConfusionMatrix

LANGCODES = ("Romanian","ro"), ("Polish", "pl"), ("German", "de"), ("Czech", "cs")

def get_kappa(cm):
  # The pandas_confusion kappa implementation crashes on some platforms,
  # so I reimplement it here.
  df = cm.to_dataframe()
  N = df.sum().sum()
  #print(N)
  sum_diag = np.trace(df)
  #print(sum_diag)
  sum_row = df.sum(axis=0)
  sum_col = df.sum(axis=1)
  p_e = float(sum(sum_row*sum_col)) / (N*N)
  #print(sum_row)
  #print(sum_col)
  #print (p_e)
  p_o = float(sum_diag) / N
  #print(p_o)
  kappa = (p_o - p_e) / (1 - p_e)
  return kappa,p_o,p_e

def print_overall_stats(by_lang,args):
  print("Counts of doubly annotated nodes") 
  node_count = len(by_lang)
  sentence_count = len(by_lang['sent_id'].value_counts())
  print("Sentence count: {}; Node count: {}".format(sentence_count, node_count))

def print_overall_iaa(by_lang, args):
  groups = (("A", "B", "R", "O", "G"),)
  if args.separate_label_groups:
    groups = (("A", "B"), ("R", "O", "G"), ("R", "G"),("A", "B","R", "O", "G"))
  for group in groups:
    print("Considering labels: " +  str(group))
    by_label = by_lang[\
      (by_lang['mt_label_x'].isin(group)) & (by_lang['mt_label_y'].isin(group))]
    print("Confusion matrix")
    cm = ConfusionMatrix(by_label['mt_label_x'], by_label['mt_label_y'], \
      true_name="annot_1", pred_name="annot_2")
    print(cm)
    kappa, p_o, p_e = get_kappa(cm)
    #print(cm.to_dataframe())
    #print(cm.stats())
    print("Kappa: %7.5f; P_o: %7.5f; P_e: %7.5f" % (kappa, p_o, p_e))

def print_iaa_sentence_detail(agree, detail_file):
#TODO sentence id, matches per sentence, pc a/b, pc r/o/g. src, tgt, ucca stats
  #sentences = agree[['sent_id', 'lang', 'annot_id_x', 'annot_id_y', 'ucca_label_x', 'mt_label_x', 'mt_label_y']]
  #sentences = sentences.groupby(['sent_id', 'lang'], as_index = False) 
  agree['match'] = agree['mt_label_x'] == agree['mt_label_y']
  group = ('A','B')
  agree['ab'] = agree['mt_label_x'].isin(group) & agree['mt_label_y'].isin(group)
  agree['abmatch'] = agree['ab'] & agree['match']

  grouped = agree.groupby(['sent_id', 'lang'], as_index=True)
  sentences = pandas.DataFrame({'accuracy' : grouped['match'].sum() / grouped['match'].size()})
  sentences['ab_accuracy'] = grouped['abmatch'].sum() / grouped['ab'].sum()


  sentences.to_csv(detail_file)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-n", "--node-file", default="nodes.csv", \
    help="CSV file containing the node data")
  parser.add_argument("--exclude-missing", default=True, action="store_true",
    help="Excluding nodes that either annotator has missed")
  parser.add_argument("--separate-label-groups", default=True, action="store_true",
    help="Treat A,B and R,G,O separately")
  parser.add_argument("--iaa-sentence-detail", help="Write detailed IAA for each sentence to the given file")
    

  args = parser.parse_args()

  allnodes = pandas.read_csv(args.node_file, converters={'node_id': str, 'parent' : str})

  # Generate records of multiply-annotated nodes
  # Join to find nodes annotated by each annotator
  merged = allnodes.merge(allnodes, on = ["node_id", "sent_id", "lang"])
  # Only want records where annotators do not much. Use an ordering
  # so we just get (pl1, pl2) and not (pl2, pl1)
  agree = merged[(merged["annot_id_x"] < merged["annot_id_y"])]
  # Optionally exclude missing annotations. Many of these are when one annotator has missed
  # the node, or the sentences. However some are legitimate, when a leaf node is not required
  # in the target language (such as an article)
  if args.exclude_missing: agree = agree[(agree["mt_label_x"] != "M") & (agree["mt_label_y"] != "M")]

  if args.iaa_sentence_detail:
    print_iaa_sentence_detail(agree, args.iaa_sentence_detail)

  for lang, code in LANGCODES:
    by_lang = agree[agree['lang'] == code]
    print ("************{}*************".format(lang))
    print_overall_stats(by_lang,args)
    print_overall_iaa(by_lang, args)
    print ()



#  alldata = pandas.read_csv("data.csv", converters={'id': str, 'parent' : str})
#  merged = alldata.merge(alldata, on = ["id", "sent", "lang"])
#  agree  = merged[(merged["user_x"] <  merged["user_y"])]
#
#  for lang, code in ("Romanian","ro"), ("Polish", "pl"):
#    print ("CONFUSION MATRIX: " + lang)
#    by_lang = agree[agree['lang'] == code]
#    
#    #Confusion Matrix
#    #print("With Missing")
#    cm = ConfusionMatrix(by_lang['mteval_x'], by_lang['mteval_y'])
#    print(cm)
#    print("Kappa: %7.5f" % cm.stats()['overall']['Kappa'])
#
#    #print("Without Missing")
#    #by_lang = by_lang[(by_lang['mteval_x'] != "M") & (by_lang['mteval_y'] != "M")]
#    #cm = ConfusionMatrix(by_lang['mteval_x'], by_lang['mteval_y'])
#    #print (cm)
#    #print("Kappa: %7.5f" % cm.stats()['overall']['Kappa'])
#
#    #Break down errors by uccalabel
#    by_lang['match'] = (by_lang['mteval_x'] == by_lang['mteval_y'])
#    by_uccalabel = by_lang.groupby(["uccalabel_x", "match"])['id'].count().unstack(1).fillna(0)
#    by_uccalabel['pc_correct'] = by_uccalabel[True] / (by_uccalabel[True] + by_uccalabel[False])
#    print("Breakdown by uccalabel")
#    print(by_uccalabel)
#
#    for label in "A", "C", "D", "E", "F", "G", "H", "L", "N", "None", "P", "R", "S", "Ti":
#      by_uccalabel = by_lang[by_lang['uccalabel_x'] == label]
#      cm  = ConfusionMatrix(by_uccalabel['mteval_x'], by_uccalabel['mteval_y'])
#      if cm.len() > 1:
#        try:
#          kappa = "%7.5f" % cm.stats()['overall']['Kappa']
#        except:
#          kappa = "Failed"
#      print("UCCA label: %3s  Kappa: %s" % (label,kappa))
#      # Comment out this to get all CMs
#      if code == "pl" and label == "H":
#        print(cm)
#
#
#    print("")
#
    


if __name__ == "__main__":
  main()

