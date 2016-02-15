#!/usr/bin/env python
from __future__ import print_function

#
# Kappa calculations, binning examples by sentence length and bleu
#

import argparse
import csv
import logging
import matplotlib.pyplot as plt
import numpy as np
import sys
import pandas



from  pandas_confusion import ConfusionMatrix

LANGCODES = ("Romanian","ro"), ("Polish", "pl")

def do_length_bins(sentences, agree, args):
  groups = (("ab", ("A", "B")), ("rog", ("R", "O", "G")), ("all", ("A", "B","R", "O", "G")))
  sentences['src_length'] = sentences['source'].str.split().apply(len)
  agree = agree.merge(sentences[['sent_id', 'src_length']], on="sent_id")
  with open(args.length_bins_file, "w") as ofh:
    writer = csv.writer(ofh)
    writer.writerow(("lang","group","bin_start","bin_end","count","kappa"))
    for lang_name,lang in LANGCODES:
      max_length = max(agree[agree['lang'] == lang]['src_length'])
      min_length = min(agree[agree['lang'] == lang]['src_length'])
      kappas = { g: [] for g,_ in groups}
      bins = []
      bin_start = min_length
      while bin_start < max_length:
        bin_end = bin_start + args.length_bins_size
        for group_name, group in groups:
          selected = agree[(agree["lang"] == lang) & \
          (agree["mt_label_x"].isin(group)) & (agree["mt_label_y"].isin(group))  & \
          (agree["src_length"] >= bin_start) & (agree["src_length"] < bin_end)]
          if len(selected):
            cm = ConfusionMatrix(selected['mt_label_x'], selected['mt_label_y'], \
              true_name="annot_1", pred_name="annot_2")
            kappa = cm.stats()['overall']['Kappa']
          else:
            kappa = 0
          writer.writerow((lang, group_name, str(bin_start), str(bin_end), len(selected), kappa))
          kappas[group_name].append(kappa)
        bins.append((bin_start,bin_end))
        bin_start += args.length_bins_size

      # Plotting to file
      fig,ax = plt.subplots()
      index = np.arange(len(bins))
      cols = ('r', 'g', 'b')
      offset = 0.0
      rects = []
      for (group,_),col in zip(groups,cols):
        rects.append(ax.bar(index + offset, kappas[group], width=0.3, color = col))
        offset += 0.3
      ax.set_yticks(np.arange(0,1.1,0.1))
      ax.set_xticks(index + 0.5)
      ax.set_xticklabels(["{}-{}".format(n,m) for n,m in bins])
      lgd = ax.legend([r[0] for r in rects],[g for g,_ in groups], loc='upper right')#, bbox_to_anchor=(1.0,1.1))
      ax.set_title("Kappa by length: {}".format(lang_name))
      ax.set_ylabel("Kappa")
      ax.set_xlabel("Source length")
      plt.savefig("{}.{}.png".format(args.length_bins_plot, lang))#, bbox_extra_artists=(lgd,), bbox_inches='tight')
      plt.clf()
    
def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-n", "--node-file", default="nodes.csv")
  parser.add_argument("-s", "--sentence-file", default="sentences.csv")

  parser.add_argument("-l", "--length-bins-file", help="Output file for length bins", default="iaa_length.csv")
  parser.add_argument("-b", "--bleu-bins-file", help="Output file for bleu bins", default="iaa_bleu.csv")
  parser.add_argument("--length-bins-size", type=int, default=8)
  parser.add_argument("--bleu-bins-size", type=float, default=0.05)
  parser.add_argument("--length-bins-plot", help = "Plot to file stem", default = "iaa_length")
  parser.add_argument("--bleu-bins-plot", help="Plot to file stem", default = "iaa_bleu")
  args = parser.parse_args()

  
  sentences = pandas.read_csv(args.sentence_file)
  nodes = pandas.read_csv(args.node_file, converters={'node_id': str, 'parent' : str})

  merged = nodes.merge(nodes, on = ["node_id", "sent_id", "lang"])
  agree = merged[(merged["annot_id_x"] < merged["annot_id_y"])]
  agree = agree[(agree["mt_label_x"] != "M") & (agree["mt_label_y"] != "M")]


  do_length_bins(sentences, agree, args)


if __name__ == "__main__":
  main()

