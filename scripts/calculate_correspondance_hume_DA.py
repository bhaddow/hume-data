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
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

import numpy as np

import extract_sentences_for_WMT_metrics_task


LANGCODES = ("Romanian","ro"), ("Polish", "pl"), ("German", "de"), ("Czech", "cs")
LANGCODES = ("Romanian","ro"),("German", "de"),

HUME_dir = "data/mturkDA"
DA_dir = "/Users/alexandrabirch/work/2016-YvetteGraham/segment-mteval/proc-hits/analysis"
fileVersion = "5"
TYPE = "raw"
TYPE = "stnd"


def main():

  corrs = []
  nums = []
  for lang, code in LANGCODES:
    #for judgements in 5, 10, 15:
    langcorrs = []
    langnums = []
    for judgements in [10]:

      UCCAfileName = HUME_dir + "/himl2015.en-" + code + ".uccascores" 
      MultUCCAfileName = HUME_dir + "/himl2015.en-" + code + ".multuccascores" 
      DAfileName = HUME_dir + "/ad-" + TYPE + "-seg-scores-" + str(judgements) + ".en-" + code + ".csv" 
      UCCAresults = pandas.read_csv(UCCAfileName, index_col=False )
      MultUCCAresults = pandas.read_csv(MultUCCAfileName, index_col=False, skip_blank_lines=False)
      DAresults = pandas.read_csv(DAfileName, sep='\s+', converters={'SID': int, 'SCR' : float})
      
      DAlist = []
      sizeDA = len(DAresults['SCR'])
      sizeUCCA = len(UCCAresults["all"])
      for i in range (0, sizeUCCA):
        x = DAresults.loc[DAresults['SID'] == i,'SCR']
        if len(x) > 0:
          DAlist.append(x.iloc[0])
        else:
          DAlist.append("")
      
      count = -1
      for score_type in extract_sentences_for_WMT_metrics_task.SCORE_TYPES:
        count += 1

        df = pandas.DataFrame({ 'UCCA' : UCCAresults[score_type],
                            'DA' : DAlist }) 
        if (score_type == "P"):
          df2 = pandas.DataFrame({ 'UCCA' : UCCAresults["S"],
                            'DA' : DAlist }) 
          df = pandas.concat([df,df2])
        elif (score_type == "S"):
          continue
        
        #df.corr(method='pearson', min_periods=1)
        # df.plot(x='UCCA', y='DA')
        df = df[df['DA'] != ""]
        corr = np.corrcoef(df['UCCA'].tolist(), df['DA'].tolist())[1,0]
        langcorrs.append(corr)
        langnums.append(df['DA'].size)
        print ("All: type " + score_type + " NumDA: " + str(judgements) 
                   + ", en-" + code + ", size " + str(len(df['DA'].tolist())) + ": " 
                   + str(corr) + " Numnodes: " + str(df['DA'].size))

        A = np.vstack([  df['UCCA'].tolist()  , np.ones(len(df['UCCA'].tolist()))]).T
        m,c = np.linalg.lstsq(A, df['DA'].tolist())[0]
        print (str(m) + " " + str(c))

      
        if (count == 0):
          #print(df.head())
          plt.rcParams.update({'font.size': 18})
          plt.plot(df['UCCA'], df['DA'], '.')
          plt.xlabel('HUME scores')
          plt.ylabel('DA scores')
          #plt.title('Human judgements for English-' + lang)
          plt.plot(df['UCCA'], m*df['UCCA'] + c, 'r', label='Fitted line')
          fname=HUME_dir + '/humevsDA.' + str(judgements) + 'en-' + code + '.pdf'
          plt.savefig(fname)
          plt.clf()

        #df = pandas.DataFrame({ 'UCCA' : MultUCCAresults[score_type],
        #                    'DA' : DAlist }) 
        ##df.corr(method='pearson', min_periods=1)
        ## df.plot(x='UCCA', y='DA')
        #df = df[df['DA'] != ""]
        #df = df[df['UCCA'] >= 0]
        #corr = np.corrcoef(df['UCCA'].tolist(), df['DA'].tolist())[1,0]
        #multicorrs.append(corr)
        #print ("Mullt: type " + score_type + " NumDA: " + str(judgements) 
        #           + ", en-" + code + ", size " + str(len(df['DA'].tolist())) + ": " 
        #           + str(corr))

      corrs.append(langcorrs)
      nums.append(langnums)

  plt.rcParams.update({'font.size': 18})
  width = 0.35
  fig, ax = plt.subplots()
  #plt.tight_layout()
  print ("HERE! ", nums)

#order: all,atomic,struct,P+S,C,H,E,A,L
#        0     1     2    3   4 5 6 7 8 
#display order: all,atomic,struct,P+S,H,A,C,E,L
  de = [corrs[1][0],corrs[1][1],corrs[1][2],corrs[1][3],corrs[1][5],corrs[1][7],corrs[1][4],corrs[1][6],corrs[1][8]]
  ro = [corrs[0][0],corrs[0][1],corrs[0][2],corrs[0][3],corrs[0][5],corrs[0][7],corrs[0][4],corrs[0][6],corrs[0][8]]
  denums = [nums[1][0],nums[1][1],nums[1][2],nums[1][3],nums[1][5],nums[1][7],nums[1][4],nums[1][6],nums[1][8]]
  ronums = [nums[0][0],nums[0][1],nums[0][2],nums[0][3],nums[0][5],nums[0][7],nums[0][4],nums[0][6],nums[0][8]]
  ind = np.arange(len(de))

  print (de)
  print (ro)
  rects1 = ax.bar(ind, de, width, color='r')
  rects2 = ax.bar(ind+width, ro, width, color='b')
  lgd = ['German', 'Romanian']

  ax.legend([rects1[0], rects2[0]], lgd, loc='upper right', borderpad=0.2)
  ax.set_xticks(ind+width)
  labels = ["all ","atomic ","struct ","P and S ","H ","A ","C ","E ","L "]
  ax.set_xticklabels(labels, rotation="vertical")
  #plt.subplots_adjust(left=0.9, right=1, top=1.6,bottom=1.5)
  plt.ylabel('Correlation')
  #plt.title('Human judgements for English-' + lang)


  #autolabel(rects1,denums,ax)
  #autolabel(rects2,ronums,ax)

  fname=HUME_dir + '/humevsDAcorrtypes.' + str(judgements) + 'en-dero.pdf'
  plt.savefig(fname)
  plt.clf()

def autolabel(rects,nums,ax):
    # attach some text labels
    count = 0
    print (nums)
    for rect in rects:
        height = rect.get_height()
        val = nums[count]
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(val),
                ha='center', va='bottom')
        count += 1

if __name__ == "__main__":
  main()

