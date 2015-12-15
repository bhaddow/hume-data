#!/usr/bin/env python
from __future__ import print_function

import pandas
from  pandas_confusion import ConfusionMatrix

def main():
  alldata = pandas.read_csv("data.csv", converters={'id': str, 'parent' : str})
  merged = alldata.merge(alldata, on = ["id", "sent", "lang"])
  agree  = merged[(merged["user_x"] != merged["user_y"])]

  for lang, code in ("Romanian","ro"), ("Polish", "pl"):
    print ("CONFUSION MATRIX: " + lang)
    by_lang = agree[agree['lang'] == code]

    print("With Missing")
    cm = ConfusionMatrix(by_lang['mteval_x'], by_lang['mteval_y'])
    print (cm)
    print("Kappa: %7.5f" % cm.stats()['overall']['Kappa'])

    print("Without Missing")
    by_lang = by_lang[(by_lang['mteval_x'] != "M") & (by_lang['mteval_y'] != "M")]
    cm = ConfusionMatrix(by_lang['mteval_x'], by_lang['mteval_y'])
    print (cm)
    print("Kappa: %7.5f" % cm.stats()['overall']['Kappa'])
    print("")



if __name__ == "__main__":
  main()

