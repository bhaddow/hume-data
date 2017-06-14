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
from iaa import get_kappa, LANGCODES

from common import NODES, SENTENCES

LOG = logging.getLogger(__name__)


def do_bins(agree, bins, field_name, csv_file, graph_file, name):
  LOG.info("Calculating kappas, binning by " +name)
  #groups = (("ab", ("A", "B")), ("rog", ("R", "O", "G")), ("all", ("A", "B","R", "O", "G")))
  groups = (("struct", ("A", "B")), ("atomic", ("R", "O", "G")))
  with open(csv_file, "w") as ofh:
    writer = csv.writer(ofh)
    writer.writerow(("lang","group","bin_start","bin_end","count","kappa"))
    for lang_name,lang in LANGCODES:
      by_lang = agree[agree["lang"] == lang]
      LOG.info("Considering " + lang_name)
      max_length = max(by_lang[field_name])
      #min_length = min(agree[agree['lang'] == lang][field_name])
      kappas = { g: [] for g,_ in groups}
      counts = { g: [] for g,_ in groups}
      for bin_start, bin_end in bins:
        LOG.debug("Bin start: {}; Bin end: {}".format(bin_start,bin_end))
        for group_name, group in groups:
          selected = by_lang[ \
          (by_lang["mt_label_x"].isin(group)) & (by_lang["mt_label_y"].isin(group))  & \
          (by_lang[field_name] >= bin_start) & (by_lang[field_name] < bin_end)]
          LOG.debug("Selected {} nodes".format(len(selected)))
          if not len(selected):
            kappa = 0
          else:
            match_labels = (selected['mt_label_x'] == selected['mt_label_y']).unique()
            if len(match_labels) == 2:
              cm = ConfusionMatrix(selected['mt_label_x'], selected['mt_label_y'], \
                true_name="annot_1", pred_name="annot_2")
              kappa,_,_ = get_kappa(cm) #cm.stats()['overall']['Kappa']
              if kappa < 0:
                print(cm)
            elif match_labels[0]:
              kappa = 1
            else:
              kappa = 0
          LOG.debug("Kappa: {}".format(kappa))
          writer.writerow((lang, group_name, str(bin_start), str(bin_end), len(selected), kappa))
          kappas[group_name].append(kappa)
          counts[group_name].append(len(selected))

      # Plotting to file
      fig,ax = plt.subplots()
      index = np.arange(len(bins))
      cols = ('r', 'b', 'g')[:len(groups)]
      offset = 0.0
      rects = []
      width = 1.0 / len(groups) - 0.03
      for (group,_),col in zip(groups,cols):
        rects.append(ax.bar(index + offset, kappas[group], width=width, color = col))
        offset += width
        for rect, count in zip(rects[-1], counts[group]):
          ax.text(rect.get_x() + rect.get_width()/2, rect.get_height(), str(count), 
              ha='center', va='bottom', size='small')
      ax.set_yticks(np.arange(0,1.1,0.1))
      ax.set_xticks(index + 0.5)
      ax.set_xlim(0,len(bins))
      ax.set_xticklabels(["{}-{}".format(n,m) for n,m in bins[:-1] + ((bins[-1][0],""),)])
      lgd = ax.legend([r[0] for r in rects],[g for g,_ in groups], loc='upper left', borderpad=0.2)#, bbox_to_anchor=(1.0,1.1))
      #ax.set_title("Kappa by {}: {}".format(name, lang_name))
      ax.set_ylabel("Kappa")
      ax.set_xlabel(name)
      graph_file_name = "{}_{}.png".format(graph_file, lang)
      plt.savefig(graph_file_name)#, bbox_extra_artists=(lgd,), bbox_inches='tight')
      plt.clf()
   

def do_bleu_bins(sentences, agree, args):
  bins = ((0,0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0))
  agree = agree.merge(sentences[['sent_id', 'bleu']].drop_duplicates(), on="sent_id")
  do_bins(agree, bins, "bleu", args.bleu_bins_file, args.bleu_bins_plot, "Sentence Bleu") 

def do_length_bins(sentences, agree, args):
  bins = ((0,15), (15, 20), (20, 25), (25, 80))
  sentences['src_length'] = sentences['source'].str.split().apply(len)
  agree = agree.merge(sentences[['sent_id', 'src_length']].drop_duplicates(),  on="sent_id")
  do_bins(agree, bins, "src_length", args.length_bins_file, args.length_bins_plot, "length") 
   
def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  parser.add_argument("-n", "--node-file", default=NODES)
  parser.add_argument("-s", "--sentence-file", default=SENTENCES)

  parser.add_argument("-l", "--length-bins-file", help="Output file for length bins", default="iaa_length.csv")
  parser.add_argument("-b", "--bleu-bins-file", help="Output file for bleu bins", default="iaa_bleu.csv")
  parser.add_argument("--length-bins-plot", help = "Plot to file stem", default = "iaa_length")
  parser.add_argument("--bleu-bins-plot", help="Plot to file stem", default = "iaa_bleu")
  args = parser.parse_args()


  # font size
  plt.rcParams.update({'font.size': 22})
  plt.rcParams.update({'figure.autolayout': True})
  
  sentences = pandas.read_csv(args.sentence_file)
  nodes = pandas.read_csv(args.node_file, converters={'node_id': str, 'parent' : str})

  merged = nodes.merge(nodes, on = ["node_id", "sent_id", "lang"])
  agree = merged[(merged["annot_id_x"] < merged["annot_id_y"])]
  agree = agree[(agree["mt_label_x"] != "M") & (agree["mt_label_y"] != "M")]


  do_bleu_bins(sentences, agree, args)
  do_length_bins(sentences, agree, args)


if __name__ == "__main__":
  main()

