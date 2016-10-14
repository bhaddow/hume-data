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

      UCCAfileName = HUME_dir + "/himl2015.en-" + code + ".uccascores" 
      DAfileNameRaw = HUME_dir + "/ad-good-raw.csv" #not standardised
      DAfileNameStd = HUME_dir + "/ad-en" + code + "-good-stnd.csv" #standardised

      UCCAresults = pandas.read_csv(UCCAfileName, header=None)
      DAresultsStd = pandas.read_csv(DAfileNameStd, sep='\s+', converters={'sid': int, 'score' : float})
      DAresultsRaw = pandas.read_csv(DAfileNameRaw, sep='\s+', converters={'sid': int, 'score' : float})
      
      DAlist = []
      sizeDA = len(DAresultsStd['score'])
      sizeUCCA = len(UCCAresults[0])
      for i in range (0, sizeUCCA):
        x = DAresultsStd.loc[DAresultsStd['sid'] == i,'score']
        if len(x) > 0:
          y = []
          for j in range (0, len(x)):
            y.append(x.iloc[j])
          DAlist.append(y)
        else:
          DAlist.append("")
      
      fname=HUME_dir + "/himl2015.en-" + code + ".stddascores" 
      stdda = open(fname, 'w')
      for scores in DAlist:
        print(",".join(map(str, scores)), file=stdda)

      DAlist = []
      for i in range (0, sizeUCCA):
        x = DAresultsRaw.loc[DAresultsRaw['sid'] == i,'score']
        if len(x) > 0:
          y = []
          for j in range (0, len(x)):
            y.append(x.iloc[j])
          DAlist.append(y)
        else:
          DAlist.append("")
      
      fname=HUME_dir + "/himl2015.en-" + code + ".rawdascores" 
      stdda = open(fname, 'w')
      for scores in DAlist:
        print(",".join(map(str, scores)), file=stdda)

if __name__ == "__main__":
  main()

