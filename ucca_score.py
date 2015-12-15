#!/usr/bin/env python
from __future__ import print_function, division

import sys
import pandas
from  pandas_confusion import ConfusionMatrix

def plain_score(alldata):
#Plain score = (correct nodes + (partially correct nodes/2) ) / all nodes(excl missing)
#alldata.loc[:,['id','user','mteval']].groupby(['user','mteval']).count()
  print ("Plain score \n\n")
  users = alldata['user'].unique()
  for user in users:
    print ("User: " , user)
    data = alldata.loc[alldata["user"] == user]
    good = data.loc[(data["mteval"]=="A") | (data["mteval"]=="G") ]
    ok = data.loc[(data["mteval"]=="O")]
    all = data.loc[(data["mteval"]!="M")]
    score = ( good["id"].count() + ok["id"].count()/2 ) / all["id"].count()
    print ("User:", user, " Plain Score: " , score) 

def span_score(alldata):
#Span score = plain score, but we take the span of the node into account
#(correct node spans + (partially correct node spans/2) ) / all node spans(excl missing)
#alldata.loc[:,['id','user','mteval']].groupby(['user','mteval']).count()
  print ("Span score \n\n")
  users = alldata['user'].unique()
  for user in users:
    print ("User: " , user)
    data = alldata.loc[alldata["user"] == user]
    sents = alldata['sent'].unique()
    good_spans = 0
    ok_spans = 0
    bad_spans = 0
    
    for sent in sents:
      print ("Sent: " , sent)
      sdata = data.loc[alldata["sent"] == sent]
      #print (sdata)
      for row in sdata.itertuples():
        children = str.split(str(row[8]))
        count = count_children(sdata,row[1],0)
        #print ("Count:", count, " row:", row[1])
#data = alldata.loc[(alldata["user"] == user) & (alldata["sent"] == sent)]
        mteval = row[6]
        if (mteval == "A" or mteval == "G"):
          good_spans += count
        elif (mteval == "O"):
          ok_spans += count
        elif (mteval != "M"):
          bad_spans += count
    score = ( good_spans + ok_spans/2 ) / (bad_spans + good_spans + ok_spans)
    print ("User:", user, " Span Score: " , score) 


#pass a dataframe with rows for one sentence by one annotator
def count_children(alldata,node,count):
  #print ("In Count Children Node:", node, " count:", count)
  data = alldata.loc[alldata["id"] == node]
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
  alldata = pandas.read_csv("data.csv", converters={'id': str, 'parent' : str})
#  alldata = pandas.read_csv("mini.csv", converters={'id': str, 'parent' : str})
  plain_score(alldata)
  span_score(alldata)



if __name__ == "__main__":
  main()

