#!/usr/bin/env python3


import argparse
import csv
import glob
import logging
import os
import os.path
import sys

import xml.etree.ElementTree as ET

from collections import Counter,namedtuple

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

#TODO: List of systems we are interested in
SYSTEMS = {\
  "cs" : ["uedin-nmt", "cu-TectoMT", "cu-chimera"],\
  "de" : ["uedin-nmt", "uedin-syntax", "uedin-pbmt"],\
  "ro" : ["uedin-nmt", "uedin-pbmt", "QT21-HimL-SysComb"],\
}


#
# How should this work?
# - Load up the source sentences, in their documents
# - For each language
#   - Add outputs from systems of interest
#   - Use Christian's line_numbers files to create an index into the sentences
# - Iterate through judgements and attach to the sentences
# - Iterate through documents in order, retrieving those which have sufficient judgements
#

class Document:
  def __init__(self, name):
    self.segments = []
    self.name = name

  def add_segment(self, segment):
    self.segments.append(segment)

  def __repr__(self):
    return "Document{{name: {}; segments: {}}}".format(self.name, self.segments)

class Segment:
  def __init__(self,source):
    self.source = source
    # each element maps system name to output sentence
    self.targets = {lang.two : {} for lang in LANGS}

  def add_translation(self,translation):
    self.targets[translation.language][translation.system] = translation

  def __repr__(self):
    return "Segment{{source: {}}}".format(self.source)

class Translation:
  def __init__(self,segment,language,system,sentence):
    self.language = language
    self.system = system
    self.sentence = sentence
    segment.add_translation(self)
    self.judgements = []

  def add_judgement(self, judgement):
    self.judgements.append(judgement)

class Judgement:
  def __init__(self, record):
    self.rankid = int(record['segmentId'])
    self.system1 = record['system1Id'].split(".")[1]
    self.system2 = record['system2Id'].split(".")[1]
    self.system1rank = record['system1rank']
    self.system2rank = record['system2rank']

  def get_systems(self):
    pair = [self.system1,self.system2]
    pair.sort()
    return tuple(pair)

    
def load_sources(documents, id_to_segment):
  for lang in LANGS:
    LOG.info("Processing source sgm for " + lang.name)
    sgm_file = "data/wmt16/newstest2016-en{}-src.en.sgm".format(lang.two)
    LOG.info("Reading source sentences from {}".format(sgm_file))
    cur_doc = None
    line_no = 1 #1-based
    line_in_doc = 0 #0-based!
    with open(sgm_file) as sfh:
      for line in sfh:
        if line.startswith("<doc"):
          start = line.find("docid") + 7
          end = line.find("\"", start)
          doc_name = line[start:end]
          if not doc_name in documents:
            cur_doc = Document(doc_name)
            documents[doc_name] = cur_doc
          else:
            cur_doc = documents[doc_name]
          line_in_doc = 0
        elif line.startswith("<seg"):
          start = line.find(">") + 1
          end = -7
          source = line[start:end]
          segment = None
          if line_in_doc >=  len(cur_doc.segments):
            # segment not there yet
            segment = Segment(source)
            cur_doc.add_segment(segment)
          else:
            segment = cur_doc.segments[line_in_doc]
          id_to_segment[(line_no,lang.two)] = segment
          line_no += 1
          line_in_doc += 1

    LOG.info("Loaded {} documents and {} segments".format(len(documents), len(id_to_segment)))

def load_system_outputs(id_to_segment):
  for lang in LANGS:
    for system in SYSTEMS[lang.two]:
      LOG.info("Loading outputs for system: {}; language: {}".format(system, lang.name))
      output_file = glob.glob("data/wmt16/en-{}/newstest2016.{}.*".format(lang.two,system))
      if len(output_file) != 1:
        raise RuntimeError("Expected single output for {}/{}, found {}".format(system, lang.name, len(output_file)))
      line_no = 1
      with open(output_file[0]) as ofh:
        for line in ofh:
          line = line[:-1]
          segment = id_to_segment[(line_no,lang.two)]
          translation = Translation(segment, lang.two, system, line)
          line_no += 1

def load_ranking_map(rankid_to_id):
  for lang in LANGS:
    line_numbers_file = "data/wmt16/en-{}/line_numbers".format(lang.two)
    LOG.info("Loading rankings map from " + line_numbers_file)
    rankid = 1
    with open(line_numbers_file) as lfh:
      for line in lfh:
        line_no = int(line[:-1])
        rankid_to_id[(rankid,lang.two)] = line_no
        rankid += 1

def load_judgements(rankid_to_id, id_to_segment):
  for lang in LANGS:
    systems = set(SYSTEMS[lang.two])
    csv_file = "data/wmt16/wmt16-dump-20160629-2326.eng-{}.csv".format(lang.three)
    LOG.info("Loading judgements from " + csv_file)
    judgement_count = 0
    with open(csv_file) as cfh:
      reader = csv.DictReader(cfh)
      for row in reader:
        judgement = Judgement(row)
        if judgement.system1 in systems and judgement.system2 in systems:
          segment = id_to_segment[(rankid_to_id[(judgement.rankid, lang.two)], lang.two)]
          segment.targets[lang.two][judgement.system1].add_judgement(judgement)
          segment.targets[lang.two][judgement.system2].add_judgement(judgement)
          judgement_count += 1
    LOG.info("Total judgements: {}".format(judgement_count))

def select_sentences(documents, max_segments):
  cfh = open("judgements.csv", "w")
  keys = []
  keys.append("segment")
  for lang in LANGS:
    for sys1 in SYSTEMS[lang.two]:
      for sys2 in SYSTEMS[lang.two]:
        if sys1 < sys2:
          keys.append("judge#{}#{}#{}".format(lang.two,sys1,sys2))
  csv_writer = csv.DictWriter(cfh,keys)
  csv_writer.writeheader()

  segments_selected = 0
  for doc_id in DOC_IDS:
    LOG.info("Considering document " + doc_id)
    document = documents[doc_id]
    for segment in document.segments:
      fields = {}
      fields['segment'] = segment.source
      min_counts = {}
      for lang in LANGS:
        judge_counts = Counter()
        systems = SYSTEMS[lang.two]
        #count judgements
        for sys1 in systems:
          for sys2 in systems:
            if sys1 != sys2:
              sys_pair = [sys1,sys2]
              sys_pair.sort()
              judge_counts[(lang.two,tuple(sys_pair))] = 0
        for target in segment.targets[lang.two].values():
          for judgement in target.judgements:
            sys_pair = judgement.get_systems()
            judge_counts[(lang.two,sys_pair)] += 1
        min_counts[lang.two] = min(judge_counts.values())
        for (lang_code, (sys1,sys2)),judge_count in judge_counts.items():
          key = "judge#{}#{}#{}".format(lang_code,sys1,sys2)
          fields[key] = int(judge_count/2)
      count = sum([value for key,value in fields.items() if key != "segment"])
      if count: csv_writer.writerow(fields)
      if count > 1:
      #  #print("Selecting : {}".format(segment))
        segments_selected += 1
        if segments_selected > max_segments:
          LOG.info("Selected {} segments, stopping".format(max_segments))
    LOG.info("Selected {} segments so far".format(segments_selected)) 


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max-segments", default=300, type=int)
    args = parser.parse_args()

    documents = {} # name to document
    id_to_segment = {} # maps (line_no, lang) to Segment object,  where line_no is in full file
    load_sources(documents, id_to_segment)

    load_system_outputs(id_to_segment)

    rankid_to_id = {} # maps (rankid,lang) to line_no
    load_ranking_map(rankid_to_id)

    load_judgements(rankid_to_id, id_to_segment)

    select_sentences(documents, args.max_segments)


if __name__ == "__main__":
  main()

