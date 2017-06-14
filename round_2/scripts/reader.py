#!/usr/bin/env python3

#
# Iterate through annotated sentences
#

import argparse
import glob
import logging
import sys

from collections import namedtuple
from xml.etree.ElementTree import ElementTree, tostring, fromstring

from ucca.convert import *

LOG = logging.getLogger(__name__)

AnnotatedSentence = namedtuple('AnnotatedSentence',
  ['sent_id', 'annot_id', 'sequence_id', 'lang', 'filename', 'ucca_annot_id', 'source', 'target', 'align',  'ucca_tree', 'mt_annotation', 'timestamp'])

ANNOTATION_KEY = {65: 'A', 66: 'B', 71 : 'G', 79 : 'O', 82 : 'R'}

def read_string(fh):
  return eval(fh.readline()).decode("utf8")

def parse_pairs(line):
  ret = []
  for field in line.split('#'):
    if not field: continue
    a,b = field.split(":")
    ret += [(int(x),int(y)) for x in a.split(",") for y in b.split(",")]
  return ret

def get_sentences(filenames):
  if not filenames: filenames = glob.glob("data/raw/*dump")
  filenames.sort()
  cs2_ids = set() # Record sentence ids annotated by cs2, since we only keep the first cs2 annotation on each sentence
  for filename in filenames:
    LOG.info("Reading from {}".format(filename))
    with open(filename) as dfh:
      while True:
        line = dfh.readline()
        if not line.startswith("==="):
          break # end of file
        #ignore first line
        line = dfh.readline()
        annot_id = read_string(dfh)
        lang = annot_id[:2]
        sequence_id = eval(dfh.readline())
        sent_id = eval(dfh.readline())
        #if int(sent_id) < 0:
        #  sent_id = str(int(sent_id) + 1600)
        mtevals = parse_pairs(read_string(dfh))
        untok_source = read_string(dfh)
        target = read_string(dfh)
        align = parse_pairs(read_string(dfh))
        # parse ucca tree
        xml = read_string(dfh)
        elem = fromstring(xml)
        passage,idMap = from_site(elem,True)
        idMap['1.1'] = '1'

        source = read_string(dfh)
        ucca_annot = read_string(dfh)
        timestamp = dfh.readline()[:-1]

        if annot_id == "cs2":
          print("cs2 annotated " + str(sent_id))
          if sent_id in cs2_ids:
             print("Already seen, skipping")
             continue
          cs2_ids.add(sent_id)

        #decode mt annotation
        invert_id_map = {int(v):k for k,v in idMap.items()}
        #FIXME Why do some mt evaluations not map to nodes?
        mt_annotation = {invert_id_map.get(node_number, None) : ANNOTATION_KEY[mt_annot] for node_number,mt_annot in mtevals}

        annot = AnnotatedSentence(sent_id, annot_id, sequence_id, lang, filename, ucca_annot, source, target, align, passage, mt_annotation, timestamp)
        yield annot




def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', nargs='+', dest='inFile', help="Input UCCAMT Eval dump files")
    args = parser.parse_args()
    
    for sent in get_sentences(args.inFile):
      print (sent)


if __name__ == "__main__":
  main()
