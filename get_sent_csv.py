#!/usr/bin/env python3

#
# Create a csv entry for each sentence, containing detail info about the sentence and its annotation
#

import argparse
import csv
import glob
import logging
import os
import sys

from collections import Counter
from reader import get_sentences, ANNOTATION_KEY

LOG = logging.getLogger(__name__)

#
# Note: the source field in the ucca dump seems to be inconsistently normalised - sometimes it contains the "@-@", and
# somtimes not.
#
def deescape(line):
  return line.replace("@-@","-").replace("&quot;",'"').replace("&apos;", "'").replace("&amp;", "&").replace(" - ", "-").replace(" n't", "n 't")

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', nargs='+', dest='inFile', help="Input UCCAMT Eval dump files")
    parser.add_argument('-o', '--outputFile',  dest='outFile', help="Output csv file", default="sentences.csv")
    args = parser.parse_args()

    # Load references and bleu
    references = {}
    bleus = {}
    sources = []
    with open("data/texts/source.en") as sfh:
      sources = [deescape(line[:-1]) for line in sfh.readlines()]
    for lang in "cs", "de", "pl", "ro":
      with open("data/texts/reference." + lang) as rfh,\
        open("data/texts/bleu." + lang) as bfh:
        line_no = 0
        for rline,bline in zip(rfh,bfh):
          references[(lang,sources[line_no])] = (rline[:-1], float(bline[:-1]))
          line_no += 1

    inFile = args.inFile
    mt_keys = list(ANNOTATION_KEY.values()) + ["M"]
    mt_colkeys = ["mteval_{}".format(key) for key in mt_keys]
    with open(args.outFile, "w") as csvfh:
      print("sent_id,annot_id,lang,source,target,reference,bleu,ucca_node_count,", file=csvfh, end="")
      print("ucca_H,", file=csvfh, end="")
      print(",".join(mt_colkeys), file=csvfh,end="")
      print(file=csvfh)
      csv_writer = csv.writer(csvfh,  lineterminator=os.linesep)
      for sent in get_sentences(inFile):
        fields = []
        fields.append(sent.sent_id)
        fields.append(sent.annot_id)
        fields.append(sent.lang)
        fields.append(sent.source)
        fields.append(sent.target)
        ref,bleu = references[(sent.lang,deescape(sent.source))]
        fields.append(ref)
        fields.append(bleu)

        # ucca nodes and annotations
        mt_eval_counts = Counter()
        ucca_counts = Counter()
        for node in sent.ucca_tree.nodes:
          node = sent.ucca_tree.nodes[node]
          if node.tag != "FN": continue
          mt_annot = sent.mt_annotation.get(node.ID, "M")
          mt_eval_counts[mt_annot] += 1
          ucca_counts[node.ftag] += 1
        fields.append(sum(mt_eval_counts.values()))
        fields.append(ucca_counts["H"])
        fields += [mt_eval_counts[key] for key in mt_keys]

        csv_writer.writerow(fields)
 
if __name__ == "__main__":
  main()

