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
    parser.add_argument('--error-details-file', help="Details of all nodes with errors", default="error-details.csv")
    parser.add_argument("--error-counts-file", help="Frequency of different errors", default="error-counts.csv")
    args = parser.parse_args()

    sentences = pandas.read_csv(args.sentenceFile)
    nodes = pandas.read_csv(args.nodeFile)


    errors = nodes[(nodes.mt_label == "R")]
    errors = errors.merge(sentences, on=("sent_id", "annot_id"), suffixes=("_word", "_sentence"))
    errors.rename(columns={'lang_word':'lang'}, inplace=True)
#    print(errors.head(), file=sys.stderr)
    
    errors.to_csv(args.error_details_file, columns=["node_id", "sent_id", "lang", "annot_id", "source_sentence", "target_sentence", \
       "source_word", "target_word", "pos"], header=True)


    #create another file with counts of source_word-target_word errors, ranked by frequency, for each language
    error_counts = pandas.DataFrame({"count" : errors.groupby(['source_word', 'target_word', 'lang']).size()})
#    print(error_counts.head(), file=sys.stderr)
    error_counts.to_csv(args.error_counts_file, header=True)
    error_counts = pandas.read_csv("error-counts.csv")
    def convert(x):
      return x.decode("utf8")
    #print(error_counts[error_counts.lang == "cs"].to_html(formatters = {"source_word" : convert, "target_word" : convert}))
    #print(error_counts[error_counts.lang == "cs"].to_html(force_unicode=True))

if __name__ == "__main__":
  main()


