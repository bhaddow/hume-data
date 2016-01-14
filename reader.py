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
  ['sent_id', 'annot_id', 'lang', 'filename', 'ucca_annot_id', 'source', 'target', 'align',  'ucca_tree', 'mt_annotation', 'timestamp'])

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
  for filename in filenames:
    LOG.info("Reading from {}".format(filename))
    with open(filename) as dfh:
      while True:
        line = dfh.readline()
        if not line.startswith("==="):
          break # end of file
        filename = read_string(dfh)
        lang = filename[-3:-1]
        annot_id = filename[-3:]
        sent_id = eval(dfh.readline())
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

        #decode mt annotation
        invert_id_map = {int(v):k for k,v in idMap.items()}
        #FIXME Why do some mt evaluations not map to nodes?
        mt_annotation = {invert_id_map.get(node_number, None) : ANNOTATION_KEY[mt_annot] for node_number,mt_annot in mtevals}

        annot = AnnotatedSentence(sent_id, annot_id, lang, filename, ucca_annot, source, target, align, passage, mt_annotation, timestamp)
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
