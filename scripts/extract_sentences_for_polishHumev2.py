#!/usr/bin/env python
from __future__ import print_function, division

import sys, string
import pandas
import numpy
from  pandas_confusion import ConfusionMatrix

SCORE_TYPES = ['all','atomic','struct','P','S','C','H','E','A','L']
LANGS = ['ro','de','cs','pl']
#LANGS = ['ro']

prefix="data/humev2"

def main():
  nodedata = pandas.read_csv("nodes.csv", converters={'node_id': str, 'parent' : str})

  #scores = {}
  #lang = {0:1,2:3}
  #scores['ro'] = lang
  sentdata = pandas.read_csv("sentences.csv", converters={'node_id': str, 'parent' : str})
  extract(sentdata)

#returning an array where have:
#dictionary with key=language, dictionary with key=sentenceid, array of hume scores

def extract(data):
    print ("Stats \n\n")

    fs = open(prefix + "/source.txt", 'w')
    ft = open(prefix + "/hypo.txt", 'w')
    fr = open(prefix + "/reference.txt", 'w')
    fi = open(prefix + "/id.txt", 'w')

    datap = data.loc[(data["annot_id"] == "pl1") | (data["annot_id"] == "pl2") ]
    ids = datap['sent_id'].unique()
  
    for id in sorted(ids):
        datasent = datap.loc[data["sent_id"] == id]

        for row_index, row in datasent.iterrows():
            fi.write('%s\n' % (row.sent_id))
            fs.write('%s\n' % (row.source))
            fr.write('%s\n' % (row.reference))
            ft.write('%s\n' % (row.target))
            break
     
    fs.close()
    ft.close()
    fr.close()
    fi.close()


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

