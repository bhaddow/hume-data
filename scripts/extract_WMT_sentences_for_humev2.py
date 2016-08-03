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

JUDGE_COUNT_THRESH = 2
MAX_LENGTH = 30 # max length of sentences selected from medical docs

Language = namedtuple('Language', ['two', 'three', 'name'])
LANGS = [ \
  Language('cs', 'cze', 'Czech'),\
  Language('de', 'deu' , 'German'),\
  Language('ro', 'ron', 'Romanian')]

#In order of preference
MED_DOC_IDS = [\
    "reuters.126785",\
    "guardian.80584",\
    "rt.com.28308",\
]

DOC_IDS = MED_DOC_IDS + [\
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
    "guardian.80559",\
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
# - Iterate through judgements and attach to the sentences
# - Iterate through documents in order, retrieving those which have sufficient judgements
#

class Document:
  def __init__(self, name):
    self.segments = []
    self.name = name

  def add_segment(self, segment):
    self.segments.append(segment)

  def get_line(self, segment):
    """Search for segment in document, give 1-based id"""
    for i,myseg in enumerate(self.segments):
      if myseg.source == segment.source:
        return i+1
    return -1

  def __repr__(self):
    return "Document{{name: {}; segments: {}}}".format(self.name, self.segments)

class Segment:
  def __init__(self,source):
    self.source = source
    # each element maps system name to output sentence
    self.targets = {lang.two : {} for lang in LANGS}
    self.refs = {} #keyed on 2-letter lang
    self.line_ids = {} #keyed on 2-letter lang

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
    self.segmentid = int(record['segmentId'])
    self.system1 = record['system1Id'].split(".")[1]
    self.system2 = record['system2Id'].split(".")[1]
    self.system1rank = record['system1rank']
    self.system2rank = record['system2rank']
    self.rankingid = int(record['rankingID'])

  def get_systems(self):
    pair = [self.system1,self.system2]
    pair.sort()
    return tuple(pair)

def sgm_file_reader(filename):
  """Generator for reading from sgm file. Returns doc_id,doc_pos(1-based),segment"""
  cur_doc_name = None
  doc_pos = 1
  with open(filename) as sfh:
    for line in sfh:
        if line.startswith("<doc"):
          start = line.find("docid") + 7
          end = line.find("\"", start)
          cur_doc_name = line[start:end]
          doc_pos = 1
        elif line.startswith("<seg"):
          start = line.find(">") + 1
          end = -7
          source = line[start:end]
          yield cur_doc_name, doc_pos, source
          doc_pos += 1
          

 
def load_sources(documents, id_to_segment):
  for lang in LANGS:
    LOG.info("Processing source sgm for " + lang.name)
    sgm_file = "data/wmt16/newstest2016-en{}-src.en.sgm".format(lang.two)
    LOG.info("Reading source sentences from {}".format(sgm_file))

    cur_doc = None
    line_no = 1 #1-based
    for doc_id, doc_pos, source in sgm_file_reader(sgm_file):
      if not doc_id in documents:
        cur_doc = Document(doc_id)
        documents[doc_id] = cur_doc
      else:
        cur_doc = documents[doc_id]
      if doc_pos > len(cur_doc.segments):
        # segment not there yet
        segment = Segment(source)
        cur_doc.add_segment(segment)
      else:
        segment = cur_doc.segments[doc_pos-1]
      id_to_segment[(line_no,lang.two)] = segment
      segment.line_ids[lang.two] = line_no
      line_no += 1

    LOG.info("Loaded {} documents and {} segments".format(len(documents), len(id_to_segment)))

def load_references(id_to_segment):
  for lang in LANGS:
    LOG.info("Processing reference sgm for " + lang.name)
    sgm_file = "data/wmt16/newstest2016-en{0}-ref.{0}.sgm".format(lang.two)
    LOG.info("Reading reference sentences from {}".format(sgm_file))
    line_no = 1
    for doc_id, doc_pos, line in sgm_file_reader(sgm_file):
      key = (line_no,lang.two)
      segment = id_to_segment.get(key,None)
      if segment:
        segment.refs[lang.two] = line
      line_no += 1


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

def load_judgements(id_to_segment):
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
          segment = id_to_segment[(judgement.segmentid, lang.two)]
          segment.targets[lang.two][judgement.system1].add_judgement(judgement)
          segment.targets[lang.two][judgement.system2].add_judgement(judgement)
          judgement_count += 1
    LOG.info("Total judgements: {}".format(judgement_count))

def select_sentences(documents, max_segments):
  selected_stem = "data/wmt16/selected"
  select_source_fh = open(selected_stem + ".source.en", "w")
  select_ref_fhs = {} # lang.two to fh
  select_sys_fhs = {} # (lang.two, sys) to fh
  select_judge_fh = open(selected_stem + ".rankings.csv", "w") 
  select_lineids_fh = open(selected_stem + ".lineids.csv", "w")

  for lang in LANGS:
    select_ref_fhs[lang.two] = open(selected_stem + ".ref." + lang.two, "w")
    for sys in SYSTEMS[lang.two]:
      select_sys_fhs[(lang.two,sys)] = \
        open("{}.{}.{}".format(selected_stem, sys, lang.two), "w")

  judge_keys = ["lang", "sentenceId", "sys1", "value1", "sys2", "value2"]
  judge_writer = csv.DictWriter(select_judge_fh,judge_keys)
  judge_writer.writeheader()

  lineid_keys = ["lang", "sentenceId", "origSentenceId", "docId", "docPos"]
  lineid_writer = csv.DictWriter(select_lineids_fh, lineid_keys)
  lineid_writer.writeheader()

  segments_selected = 0
  for doc_id in DOC_IDS:
    LOG.info("Considering document " + doc_id)
    document = documents[doc_id]
    for segment in document.segments:
      judge_records = []
      for lang in LANGS:
        systems = SYSTEMS[lang.two]
        #extract  judgements
        for target in segment.targets[lang.two].values():
          for judgement in target.judgements:
            if judgement.system1 < judgement.system2:
              record = {'lang' : lang.two, 'sentenceId' : segments_selected+1, \
                "sys1" : judgement.system1, "sys2" : judgement.system2, \
                "value1" : judgement.system1rank, "value2" : judgement.system2rank,\
                }
              judge_records.append(record)

      # Segments selected if they are medical, or if have sufficient judgements
      if len(judge_records)  >= JUDGE_COUNT_THRESH or \
          (doc_id in MED_DOC_IDS and len(segment.source.split()) <= MAX_LENGTH) :
        for rec in judge_records:
          judge_writer.writerow(rec)
        print(segment.source, file=select_source_fh)
        for lang in LANGS:
          print(segment.refs[lang.two], file=select_ref_fhs[lang.two])
          lineid_fields = {"lang" : lang.two, "sentenceId" : segments_selected+1, "docId" : doc_id}
          lineid_fields["docPos"] = document.get_line(segment)
          lineid_fields['origSentenceId'] = segment.line_ids[lang.two]
          lineid_writer.writerow(lineid_fields)
          for sys in SYSTEMS[lang.two]:
            translation = segment.targets[lang.two][sys]
            print(translation.sentence, file=select_sys_fhs[(lang.two,sys)])
        segments_selected += 1
        if segments_selected > max_segments:
          LOG.info("Selected {} segments, stopping".format(max_segments))
          return
    LOG.info("Selected {} segments so far".format(segments_selected)) 


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max-segments", default=300, type=int)
    args = parser.parse_args()

    documents = {} # name to document
    id_to_segment = {} # maps (line_no, lang) to Segment object,  where line_no is in full sgm file
    load_sources(documents, id_to_segment)
    
    load_references(id_to_segment)

    load_system_outputs(id_to_segment)

    load_judgements(id_to_segment)

    select_sentences(documents, args.max_segments)


if __name__ == "__main__":
  main()

