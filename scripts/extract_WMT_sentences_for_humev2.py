#!/usr/bin/env python3


import argparse
import csv
import glob
import logging
import os
import os.path
import sys

import xml.etree.ElementTree as ET

from collections import namedtuple

LOG = logging.getLogger(__name__)

Language = namedtuple('Language', ['two', 'three', 'name'])
LANGS = [ \
  Language('cs', 'cze', 'Czech'),\
  Language('de', 'deu' , 'German'),\
  Language('ro', 'ron', 'Romanian')]

#In order of preference
DOC_IDS = [\
    "reuters.126785",\
    "guardian.80584",\
    "telegraph.237035",\
    "abcnews.151610",\
    "abcnews.151623",\
    "bbc.184143",\
    "bbc.184189",\
    "bbc.184507",\
    "brisbanetimes.com.au.80482",\
    "cbsnews.99290",\
    "csmonitor.com.17899",\
    "csmonitor.com.17945",\
    "dailymail.co.uk.117611",\
    "dailymail.co.uk.117616",\
    "dailymail.co.uk.117660",\
    "euronews-en.68857",\
    "foxnews.49843",\
    "guardian.80536",\
    "guardian.80559",\
    "guardian.80573",\
    "guardian.80762",\
    "guardian.80776",\
    "latimes.120721",\
    "latimes.120727",\
    "latimes.120779",\
    "news.com.au.655751",\
    "news.com.au.656039",\
    "nytimes.50946",\
    "reuters.126606",\
    "rt.com.28303",\
    "rt.com.28308",\
    "scotsman.58691",\
    "scotsman.58710",\
    "sky.com.12411",\
    "smh.com.au.134327",\
    "smh.com.au.134349",\
    "smh.com.au.134355",\
    "stv.tv.16044",\
    "telegraph.236835",\
    "telegraph.236852",\
    "thelocal.26889",\
    "thelocal.26922",\
    "xinhuanet.com.20707",\
]

#TODO 
SYSTEMS = {\
  "cs" : [],\
  "de" : [],\
  "ro" : [],\
}

def has_sufficient_judgements(line_no, systems):
  return True

def select_sentences(lang, source_segs, max_segments):
   # Iterate through documents in order of preference, until the required number of sentences are obtained.
    src_fh = open("data/wmt16/selected.source.en-{}.en".format(lang.two), "w")

    chosen = 0
    for doc_id  in DOC_IDS:
      for segment,line_no in source_segs[doc_id]:
        if has_sufficient_judgements(line_no, None):
          print(segment, file=src_fh)
          chosen += 1
          if chosen >= max_segments:
            return


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max-segments", default=300, type=int)
    args = parser.parse_args()

    for lang in LANGS:
      LOG.info("Processing " + lang.name)

      # Load sgm file
      source_segs = {} # map doc id to list of (source sentence, line number) pairs
      sgm_file = "data/wmt16/newstest2016-en{}-src.en.sgm".format(lang.two)
      LOG.debug("Reading " + sgm_file)
      cur_doc = None
      line_no = 0
      with open(sgm_file) as sfh:
        for line in sfh:
          if line.startswith("<doc"):
            start = line.find("docid") + 7
            end = line.find("\"", start)
            cur_doc = line[start:end]
          elif line.startswith("<seg"):
            start = line.find(">") + 1
            end = -7
            segment = line[start:end]
            segments_by_doc = source_segs.get(cur_doc, [])
            segments_by_doc.append((segment,line_no))
            source_segs[cur_doc] = segments_by_doc
            line_no += 1

      # Load system data and judgements
      # For each source sentence, we collect:
        # target sentences for each system of interest
        # judgements
      target_segs = {} # map source_id to list of tuples of (hit-id, system->segment map)
      for hit_file in glob.glob("data/wmt16/newstask-en-{}*fixed".format(lang.two)):
        LOG.debug("Loading HITs from " + hit_file)
        hit_root = ET.parse(open(hit_file)).getroot()
        segs =  hit_root.findall(".//seg")
        for seg in segs:
          source = seg.find(".//source")
          source_id = int(source.attrib['id'])
          hits = target_segs.get(source_id, [])
          hit_id = -1 #TODO: need to use this to map to judgements
          targets = {}
          hits.append([hit_id,targets])
          for target in seg.findall(".//translation"):
            system = target.attrib['system']
            system = system.split(".")[1]
            segment = target.text
            targets[system] = segment
          target_segs[source_id] = hits
          print (target_segs)
          sys.exit(0)
      LOG.debug("Loaded HITs for {} segments".format(len(target_segs)))

      # select
      select_sentences(lang, source_segs, args.max_segments)
 

if __name__ == "__main__":
  main()

