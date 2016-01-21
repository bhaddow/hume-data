#!/usr/bin/env python
from __future__ import print_function, division

import sys
import pandas
from  pandas_confusion import ConfusionMatrix

def stats(alldata):

def plain_score(alldata):
#Plain score = (correct nodes + (partially correct nodes/2) ) / all nodes(excl missing)
#alldata.loc[:,['id','user','mt_label']].groupby(['user','mt_label']).count()
  print ("Plain score \n\n")
  users = alldata['annot_id'].unique()
  for user in users:
    print ("User: " , user)
    data = alldata.loc[alldata["annot_id"] == user]

    dataS = data.loc[(data["mt_label"]=="A") | (data["mt_label"]=="B") ]
    good = dataS.loc[(dataS["mt_label"]=="A") ]
    all = dataS.loc[(dataS["mt_label"]!="M")]
    score = ( good["node_id"].count() ) / all["node_id"].count()
    print ("User:", user, " Plain Structural Score: " , score) 

    dataL = data.loc[(data["mt_label"]=="R") | (data["mt_label"]=="G") | (data["mt_label"]=="O") ]
    good = dataL.loc[(dataL["mt_label"]=="G") ]
    ok = dataL.loc[(dataL["mt_label"]=="O")]
    all = dataL.loc[(dataL["mt_label"]!="M")]
    score = ( good["node_id"].count() + ok["node_id"].count()/2 ) / all["node_id"].count()
    print ("User:", user, " Plain Lexical Score: " , score) 

    data = alldata.loc[alldata["annot_id"] == user]
    good = data.loc[(data["mt_label"]=="A") | (data["mt_label"]=="G") ]
    ok = data.loc[(data["mt_label"]=="O")]
    all = data.loc[(data["mt_label"]!="M")]
    score = ( good["node_id"].count() + ok["node_id"].count()/2 ) / all["node_id"].count()
    print ("User:", user, " Plain Score: " , score) 

def span_score(alldata):
#Span score = plain score, but we take the span of the node into account
#(correct node spans + (partially correct node spans/2) ) / all node spans(excl missing)
#alldata.loc[:,['id','user','mt_label']].groupby(['user','mt_label']).count()
  print ("Span score \n\n")
  users = alldata['annot_id'].unique()
  for user in users:
    print ("User: " , user)
    data = alldata.loc[alldata["annot_id"] == user]
    sents = alldata['sent_id'].unique()
    good_spans = 0
    ok_spans = 0
    bad_spans = 0
    
    for sent in sents:
      print ("Sent: " , sent)
      sdata = data.loc[alldata["sent_id"] == sent]
      #print (sdata)
      for row in sdata.itertuples():
        children = str.split(str(row[8]))
        count = count_children(sdata,row[1],0)
        #print ("Count:", count, " row:", row[1])
#data = alldata.loc[(alldata["user"] == user) & (alldata["sent"] == sent)]
        mt_label = row[6]
        if (mt_label == "A" or mt_label == "G"):
          good_spans += count
        elif (mt_label == "O"):
          ok_spans += count
        elif (mt_label != "M"):
          bad_spans += count
    score = ( good_spans + ok_spans/2 ) / (bad_spans + good_spans + ok_spans)
    print ("User:", user, " Span Score: " , score) 


#pass a dataframe with rows for one sentence by one annotator
def count_children(alldata,node,count):
  #print ("In Count Children Node:", node, " count:", count)
  data = alldata.loc[alldata["node_id"] == node]
  if data["children"].count() == 0:
    print ("WARN missing childnode:",node)
    return count
  children = data["children"].iat[0]
  children = str.split(children)
  for child in children: 
    if child[0:1] == "0": #Then this is a terminal
      count += 1
    else: #Then must recurse
      count = count_children(alldata,child,count)
  #print ("Return count:", count)
  return count


def main():
  alldata = pandas.read_csv("nodes.csv", converters={'node_id': str, 'parent' : str})
#  alldata = pandas.read_csv("mini.csv", converters={'id': str, 'parent' : str})
  plain_score(alldata)
  span_score(alldata)



if __name__ == "__main__":
  main()

