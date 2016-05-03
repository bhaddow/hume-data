#!/usr/bin/env python
from __future__ import print_function, division

import sys
import pandas
from  pandas_confusion import ConfusionMatrix


prefix="data/mturkDA/himl2015"

def extract(alldata):
  print ("Stats \n\n")
  for lang in ('ro','de','cs','pl'):
    data = alldata.loc[alldata["lang"] == lang]
    ids = alldata['sent_id'].unique()
    print ("Lang: " , lang)
    lang_pair = "en-" + lang

    fref = open(prefix + "." + lang_pair + ".ref." + lang, 'w')
    ftrans = open(prefix + "." + lang_pair + ".trans." + lang, 'w')
    fid = open(prefix + "." + lang_pair + ".uccaids" , 'w')
    fsource = open(prefix + "." + lang_pair + ".en", 'w')

    for id in sorted(ids):

      datasent = data.loc[data["sent_id"] == id]
      found = 0
      for row_index, row in datasent.iterrows():
        found = 1
        fid.write('%s\n' % (row.sent_id))
        fsource.write('%s\n' % (row.source))
        fref.write('%s\n' % (row.reference))
        ftrans.write('%s\n' % (row.target))
        break
      
      if found == 0:
        print ("missing row" + str(id)) 


    ftrans.close()
    fsource.close()
    fref.close()
    fid.close()


def main():
  alldata = pandas.read_csv("sentences.csv", converters={'node_id': str, 'parent' : str})
  extract(alldata)



if __name__ == "__main__":
  main()

