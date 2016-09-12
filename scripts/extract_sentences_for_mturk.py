#!/usr/bin/env python
from __future__ import print_function, division

import sys
import pandas
from  pandas_confusion import ConfusionMatrix

import extract_sentences_for_WMT_metrics_task


LANGS = ['ro','de','cs','pl']
#LANGS = ['ro']
prefix="data/mturkDA/himl2015"

def extract(alldata, scores):
  print ("Stats \n\n")
  for lang in LANGS:
    data = alldata.loc[alldata["lang"] == lang]
    ids = alldata['sent_id'].unique()
    print ("Lang: " , lang)
    lang_pair = "en-" + lang

    fref = open(prefix + "." + lang_pair + ".ref." + lang, 'w')
    ftrans = open(prefix + "." + lang_pair + ".trans." + lang, 'w')
    fid = open(prefix + "." + lang_pair + ".uccaids" , 'w')
    fscore = open(prefix + "." + lang_pair + ".uccascores" , 'w')
    fscore.write(",".join(extract_sentences_for_WMT_metrics_task.SCORE_TYPES)
    fmultscore = open(prefix + "." + lang_pair + ".multuccascores" , 'w')
    fmultscore.write(",".join(extract_sentences_for_WMT_metrics_task.SCORE_TYPES)
    fsource = open(prefix + "." + lang_pair + ".en", 'w')

    for id in sorted(ids):



      datasent = data.loc[data["sent_id"] == id]
      found = 0
      for row_index, row in datasent.iterrows():
        found = 1



        fid.write('%s\n' % (row.sent_id))
        fsource.write('%s\n' % (row.source))
        fref.write('%s\n' % (row.reference))
        if row.sent_id in scores[lang].keys():
          score = scores[lang][row.sent_id]
          #print ("Found " + str(row.sent_id) + " score " + str(score))
          for score_type in extract_sentences_for_WMT_metrics_task.SCORE_TYPES:
            fscore.write('%s,' % score[0][score_type])
            if score[1]: #if not empty
              fmultscore.write('%s,' % score[1][score_type])
        else:
          print ("Not Found")
        fscore.write('\n')
        fmultscore.write('\n')
        ftrans.write('%s\n' % (row.target))
        break
      
      if found == 0:
        print ("missing row" + str(id)) 


    ftrans.close()
    fscore.close()
    fmultscore.close()
    fsource.close()
    fref.close()
    fid.close()


def main():

  nodedata = pandas.read_csv("nodes.csv", converters={'node_id': str, 'parent' : str})
  scores = extract_sentences_for_WMT_metrics_task.score(nodedata)

  alldata = pandas.read_csv("sentences.csv", converters={'node_id': str, 'parent' : str})
  extract(alldata, scores)


if __name__ == "__main__":
  main()

