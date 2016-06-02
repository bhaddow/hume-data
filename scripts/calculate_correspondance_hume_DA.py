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
TYPE = "raw"
TYPE = "stnd"


def main():

  for lang, code in LANGCODES:
    for judgements in 5, 10, 15:

      UCCAfileName = HUME_dir + "/himl2015.en-" + code + ".uccascores" 
      DAfileName = HUME_dir + "/ad-" + TYPE + "-seg-scores-" + str(judgements) + ".en-" + code + ".csv" 

      UCCAresults = pandas.read_csv(UCCAfileName, header=None)
      DAresults = pandas.read_csv(DAfileName, sep='\s+', converters={'SID': int, 'SCR' : float})
      
      DAlist = []
      sizeDA = len(DAresults['SCR'])
      sizeUCCA = len(UCCAresults[0])
      for i in range (0, sizeUCCA):
        x = DAresults.loc[DAresults['SID'] == i,'SCR']
        if len(x) > 0:
          DAlist.append(x.iloc[0])
        else:
          DAlist.append("")
      
      df = pandas.DataFrame({ 'UCCA' : UCCAresults[0],
                          'DA' : DAlist }) 
      
      
      df.corr(method='pearson', min_periods=1)
      
     # df.plot(x='UCCA', y='DA')
      df = df[df['DA'] != ""]
      
      print ("Correference HUME DA for " + str(judgements) + " judge, en-" + code + ", size " + str(len(df['DA'].tolist())) + ": " 
                   + str(np.corrcoef(df['UCCA'].tolist(), df['DA'].tolist())[1,0]))

      A = np.vstack([  df['UCCA'].tolist()  , np.ones(len(df['UCCA'].tolist()))]).T
      m,c = np.linalg.lstsq(A, df['DA'].tolist())[0]
      print (str(m) + " " + str(c))
      
      
      #print(df.head())
      plt.plot(df['UCCA'], df['DA'], '.')
      plt.xlabel('HUME scores')
      plt.ylabel('Averaged Direct Assesment scores')
      plt.title('Human judgements for English-' + lang)
      plt.plot(df['UCCA'], m*df['UCCA'] + c, 'r', label='Fitted line')

      
      fname=HUME_dir + '/humevsDA.' + str(judgements) + 'en-' + code + '.pdf'
      plt.savefig(fname)

      plt.clf()



if __name__ == "__main__":
  main()

