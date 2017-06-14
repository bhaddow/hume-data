#!/usr/bin/env python
from __future__ import print_function, division

import sys, string
import pandas
import numpy
from  pandas_confusion import ConfusionMatrix

SCORE_TYPES = ['all','atomic','struct','P','S','C','H','E','A','L']
LANGS = ['ro','de','cs','pl']
#LANGS = ['ro']

prefix="data/wmtmetrics/himl2015"

def main():
  nodedata = pandas.read_csv("nodes.csv", converters={'node_id': str, 'parent' : str})
  scores = score(nodedata)

  #scores = {}
  #lang = {0:1,2:3}
  #scores['ro'] = lang
  sentdata = pandas.read_csv("sentences.csv", converters={'node_id': str, 'parent' : str})
  extract(sentdata, scores)

def score(nodedata):
  results = {}
  for lang in LANGS:
    #print ("HERE " + lang)
    langDict = {}
    data = nodedata.loc[nodedata["lang"] == lang]
    ids = data['sent_id'].unique()
  
    for id in sorted(ids):
      score_all = {}
      score_mult = {}
      for score_type in SCORE_TYPES:
        datasent = data.loc[data["sent_id"] == id]
        annotids = datasent['annot_id'].unique()
        datacurr = datasent
      
        if (score_type == 'all'):
          datacurr = datasent
        elif (score_type == 'atomic'):
          datacurr = datasent.loc[(data["mt_label"] == "G")|(data["mt_label"] == "R")|(data["mt_label"] == "O")]
        elif (score_type == 'struct'):
          datacurr = datasent.loc[ (data["mt_label"] == "A")|(data["mt_label"] == "B") ]
        else:
          datacurr = datasent.loc[(data["ucca_label"] == score_type) ]
          
      
        anodes = datacurr.loc[(datacurr["mt_label"]=="A")].count()[0]
        bnodes = datacurr.loc[(datacurr["mt_label"]=="B")].count()[0]
        gnodes = datacurr.loc[(datacurr["mt_label"]=="G")].count()[0]
        onodes = datacurr.loc[(datacurr["mt_label"]=="O")].count()[0]
        rnodes = datacurr.loc[(datacurr["mt_label"]=="R")].count()[0]

        div = (anodes+bnodes+gnodes+rnodes+onodes)
        if div == 0:
          scr = 0
        else: 
          scr = (anodes + gnodes + onodes/2)*1.0 / div
        #print ("HERE: ",scr," from ",anodes," ",bnodes," ",gnodes," ",onodes," ",rnodes)
        score_all[score_type] = scr
        flag = 0
        if (len(annotids) >=2):
          flag = 1
          score_mult[score_type] = scr
        print ("Lang:", lang, " Sent:", id, " Score type: " , score_type, " score: ", score_all[score_type], " score mult:", flag ) 

      langDict[id] = [score_all, score_mult]

    results[lang] = langDict

  return results

#returning an array where have:
#dictionary with key=language, dictionary with key=sentenceid, array of hume scores

def extract(alldata, scores):
  print ("Stats \n\n")
  for lang in ('ro','de','cs','pl'):
    (listsrc, listsys, listref) = read_sourcefiles(lang)
    data = alldata.loc[alldata["lang"] == lang]
    ids = alldata['sent_id'].unique()
    print ("Lang: " , lang)
    lang_pair = "en-" + lang

    fcsv = open(prefix + "." + lang_pair + ".hume.csv", 'w')
    fcsv.write("sent_id\tsource\treference\ttarget\tscore\tsource_debug\tref_debug\ttarget_debug\n")

    for id in range(0, len(listsrc)):
    #for id in sorted(ids):

      fcsv.write('\"%s \"\t' % (id))
      fcsv.write('\"%s \"\t' % (listsrc[id].rstrip()))
      fcsv.write('\"%s \"\t' % (listref[id].rstrip()))
      fcsv.write('\"%s \"\t' % (listsys[id].rstrip()))
      if id + 1 in scores[lang].keys():
        score = scores[lang][id + 1]
        print ("Found " + str(id + 1) + " score " + str(score))
      else: 
        score = ""

      fcsv.write('\"%s \"\t' % (score))

      datasent = data.loc[data["sent_id"] == id + 1]
      found = 0
      for row_index, row in datasent.iterrows():
        found = 1
        #fcsv.write('\"%s \"\t' % (row.sent_id))
        fcsv.write('\"%s \"\t' % (row.source))
        fcsv.write('\"%s \"\t' % (row.reference))
        fcsv.write('\"%s \"\t' % (row.target))
     
        break
      
      #if found == 0:
      #  print ("missing row" + str(id)) 
      fcsv.write('\n')


    fcsv.close()

def read_sourcefiles(lang):
  dir = "data/texts/"
  listsrc = read_file(dir + "source.en")
  listsys = read_file(dir + "system." + lang)
  listref = read_file(dir + "reference." + lang)
  return (listsrc, listsys, listref) 

def read_file(fileName):
  lines = []
  try:
    inFh = open(fileName, "r")
    lines = inFh.readlines()
    for line in lines:
      line = line.strip('\n')
    inFh.close()
  except IOError:
    print ("I/O error " + fileName) 

  return lines


if __name__ == "__main__":
  main()

