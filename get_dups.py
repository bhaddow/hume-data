#!/usr/bin/env python3

#
# Find duplicate entries in the data
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

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', nargs='+', dest='inFile', help="Input UCCAMT Eval dump files")
    parser.add_argument('-o', '--outputFile',  dest='outFile', help="Output csv file", default="sentences.csv")
    args = parser.parse_args()

    sentences = {} #key is (annot_id,target)

    for sent in get_sentences(args.inFile):
      key = (sent.annot_id, sent.target)
      if key in sentences:
        print("DUPLICATE")
        print (sent.filename, "|||", sent.annot_id, "|||", sent.target, "|||", sent.timestamp)
        print (sentences[key].filename, "|||", sentences[key].annot_id, "|||", sentences[key].target, "|||", sentences[key].timestamp)
        print ()
      else:
        sentences[key] = sent

if __name__ == "__main__":
  main()

