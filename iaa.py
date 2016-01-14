#!/usr/bin/env python
from __future__ import print_function

import pandas
from  pandas_confusion import ConfusionMatrix

def main():
#  alldata = pandas.read_csv("data.csv", converters={'id': str, 'parent' : str})
#  merged = alldata.merge(alldata, on = ["id", "sent", "lang"])
#  agree  = merged[(merged["user_x"] <  merged["user_y"])]
#
#  for lang, code in ("Romanian","ro"), ("Polish", "pl"):
#    print ("CONFUSION MATRIX: " + lang)
#    by_lang = agree[agree['lang'] == code]
#    
#    #Confusion Matrix
#    #print("With Missing")
#    cm = ConfusionMatrix(by_lang['mteval_x'], by_lang['mteval_y'])
#    print(cm)
#    print("Kappa: %7.5f" % cm.stats()['overall']['Kappa'])
#
#    #print("Without Missing")
#    #by_lang = by_lang[(by_lang['mteval_x'] != "M") & (by_lang['mteval_y'] != "M")]
#    #cm = ConfusionMatrix(by_lang['mteval_x'], by_lang['mteval_y'])
#    #print (cm)
#    #print("Kappa: %7.5f" % cm.stats()['overall']['Kappa'])
#
#    #Break down errors by uccalabel
#    by_lang['match'] = (by_lang['mteval_x'] == by_lang['mteval_y'])
#    by_uccalabel = by_lang.groupby(["uccalabel_x", "match"])['id'].count().unstack(1).fillna(0)
#    by_uccalabel['pc_correct'] = by_uccalabel[True] / (by_uccalabel[True] + by_uccalabel[False])
#    print("Breakdown by uccalabel")
#    print(by_uccalabel)
#
#    for label in "A", "C", "D", "E", "F", "G", "H", "L", "N", "None", "P", "R", "S", "Ti":
#      by_uccalabel = by_lang[by_lang['uccalabel_x'] == label]
#      cm  = ConfusionMatrix(by_uccalabel['mteval_x'], by_uccalabel['mteval_y'])
#      if cm.len() > 1:
#        try:
#          kappa = "%7.5f" % cm.stats()['overall']['Kappa']
#        except:
#          kappa = "Failed"
#      print("UCCA label: %3s  Kappa: %s" % (label,kappa))
#      # Comment out this to get all CMs
#      if code == "pl" and label == "H":
#        print(cm)
#
#
#    print("")
#
    


if __name__ == "__main__":
  main()

