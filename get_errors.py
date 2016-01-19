#!/usr/bin/env python
from __future__ import print_function

#
# Extract all errors - i.e. all nodes marked as red
#

import argparse
import logging
import os
import pandas
import sys


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sentenceFile',   help="Sentence csv file", default="sentences.csv")
    parser.add_argument('-n', '--nodeFile',  help="Node csv file", default="nodes.csv")
    args = parser.parse_args()

    sentences = pandas.read_csv(args.sentenceFile)
    nodes = pandas.read_csv(args.nodeFile)


    errors = nodes[(nodes.mt_label == "R")]
    errors = errors.merge(sentences, on=("sent_id", "annot_id"), suffixes=("_word", "_sentence"))
    errors.rename(columns={'lang_word':'lang'}, inplace=True)
    print(errors.head(), file=sys.stderr)
    
    errors.to_csv(sys.stdout, columns=["node_id", "sent_id", "lang", "annot_id", "source_sentence", "target_sentence", \
       "source_word", "target_word", "pos"])


    #TODO: create another file with counts of source_word-target_word errors, ranked by frequency, for each language

if __name__ == "__main__":
  main()


