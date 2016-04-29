#!/usr/bin/env python
from __future__ import print_function, division

import sys
import pandas
from  pandas_confusion import ConfusionMatrix


prefix="himl2015"

def main():
  nodedata = pandas.read_csv("nodes.csv", converters={'node_id': str, 'parent' : str})
  scores = score(nodedata)

  sentdata = pandas.read_csv("sentences.csv", converters={'node_id': str, 'parent' : str})
  extract(sentdata, scores)

def score(nodedata):
  results = {}
  for lang in ('ro','de','cs','pl'):
    langDict = {}
    data = nodedata.loc[nodedata["lang"] == lang]
    ids = data['sent_id'].unique()
  
    for id in sorted(ids):
      datasent = data.loc[data["sent_id"] == id]
      
      g = 0
      o = 0
      a = 0
      for row_index, row in datasent.iterrows():
        
        good = datasent.loc[(datasent["mt_label"]=="A") | (data["mt_label"]=="G") ]
        ok = datasent.loc[(datasent["mt_label"]=="O")]
        all = datasent.loc[(datasent["mt_label"]!="M")]
        g += good["node_id"].count()
        o += ok["node_id"].count()
        a += all["node_id"].count()

      
      score = (g + o/2) / a
      #print ("Lang:", lang, " Sent:", id, " Plain Score: " , score) 

      langDict[id] = score

    results[lang] = langDict

  return results

#returning an array where have:
#dictionary with key=language, dictionary with key=sentenceid, array of hume scores

def extract(alldata, scores):
  print ("Stats \n\n")
  for lang in ('ro','de','cs','pl'):
    data = alldata.loc[alldata["lang"] == lang]
    ids = alldata['sent_id'].unique()
    print ("Lang: " , lang)
    lang_pair = "en-" + lang

    fcsv = open(prefix + "." + lang_pair + ".hume.csv", 'w')
    fcsv.write("sent_id, source, reference, target, score\n")

    for id in sorted(ids):

      datasent = data.loc[data["sent_id"] == id]
      found = 0
      for row_index, row in datasent.iterrows():
        found = 1
        fcsv.write('\"%s \",' % (row.sent_id))
        fcsv.write('\"%s \",' % (row.source))
        fcsv.write('\"%s \",' % (row.reference))
        fcsv.write('\"%s \",' % (row.target))
        fcsv.write('\"%s\"\n' % (scores[lang][id]))
     
        break
      
      if found == 0:
        print ("missing row" + str(id)) 


    fcsv.close()




if __name__ == "__main__":
  main()

