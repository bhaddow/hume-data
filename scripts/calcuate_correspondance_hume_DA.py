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

HUME_dir = "data/mturkDA"
DA_dir = "/Users/alexandrabirch/work/2016-YvetteGraham/segment-mteval/proc-hits/analysis"


def main():

  for lang, code in LANGCODES:

    UCCAfileName = HUME_dir + "/himl2015.en-" + code + ".uccascores" 
    DAfileName = DA_dir + "/ad-raw-seg-scores-5.en-" + code + ".csv" 

    UCCAresults = pandas.read_csv(UCCAfileName, header=None)
    DAresults = pandas.read_csv(DAfileName, sep='\s+', converters={'SID': int, 'SCR' : float})
    
    DAlist = []
    sizeDA = len(DAresults['SCR'])
    sizeUCCA = len(UCCAresults[0])
    for i in range (0, sizeUCCA):
      print ("I = " + str(i))
      x = DAresults.loc[DAresults['SID'] == i,'SCR']
      if len(x) > 0:
        DAlist.append(x.iloc[0])
      else:
        DAlist.append("")
    

    df = pandas.DataFrame({ 'UCCA' : UCCAresults[0],
                        'DA' : DAlist }) 

    
    df.corr(method='pearson', min_periods=1)

    df.plot(x='UCCA', y='DA')
    fname='test.pdf'
    plt.savefig(fname)


if __name__ == "__main__":
  main()

