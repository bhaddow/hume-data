#!/usr/bin/env python

#
# Calculate some general stats about the annotation
#

from __future__ import print_function

import argparse
import logging
import sys
import pandas 
import matplotlib.pyplot as plt

import numpy as np

LANGCODES = ("Romanian","ro"), ("Polish", "pl"), ("German", "de"), ("Czech", "cs")
LANGCODES = ("Romanian","ro"),("German", "de"),

HUME_dir = "data/mturkDA"
DA_dir = "/Users/alexandrabirch/work/2016-YvetteGraham/segment-mteval/proc-hits/analysis"
fileVersion = "5"


def main():

  for lang, code in LANGCODES:

      sentFileName = HUME_dir + "/himl2015.en-" + code + ".en" 
      daFileName = HUME_dir + "/himl2015.en-" + code + ".stddascores" 

      sentData = read_file(sentFileName)
      daData = read_file(daFileName)
 
      
      sentLenData = []
      daVarData = []
      for i in range (0, len(sentData)):
        sent = sentData[i]
        wordList = sent.split(' ')

        das = daData[i]
        daList = das.split(',')
        if (len(daList) > 0) and (daList[0] != ""):
          daVar = np.var(map(float, daList))
          daVarData.append(daVar)        
          sentLenData.append(len(wordList))
      
      plt.plot(sentLenData, daVarData, '.')
      plt.xlabel('Sentence Length')
      plt.ylabel('Variance of DA scores')
      plt.title('Variance of DA scores for English-' + lang )
      
      fname=HUME_dir + '/sentLenvsDaVarStd.en-' + code + '.pdf'
      plt.savefig(fname)

      plt.clf()
 

      


def read_file(fileName):
  lines = []
  clean = []
  try:
    inFh = open(fileName, "r")
    lines = inFh.readlines()
    for line in lines:
      line = line.strip('\n')
      clean.append(line)
    inFh.close()
  except IOError:
    print ("I/O error " + fileName) 

  return clean 


if __name__ == "__main__":
  main()

