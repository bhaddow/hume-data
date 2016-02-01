#!/usr/bin/env python
from __future__ import print_function

import cgi
import cgitb
import pandas

cgitb.enable()

def main():
  print("Content-Type: text/html")
  print()

  print("<head><meta charset=\"UTF-8\">")
  print("<title>Red-green confusions amongst annotators</title>")
  print("</head>")
  print("<BODY>")
  print("Nodes which one annotator marked green, the other red<br><br>")

  nodes = pandas.read_csv("nodes.csv")
  merged = nodes.merge(nodes, on = ["node_id", "sent_id", "lang"])
  agree = merged[(merged["annot_id_x"] < merged["annot_id_y"])]
  agree = agree[((agree["mt_label_x"] == "R") &  (agree["mt_label_y"] == "G")) | \
                    ((agree["mt_label_x"] == "G") &  (agree["mt_label_y"] == "R"))]

  counts = pandas.DataFrame({"count" : agree.groupby(["source_x", "target_x", "lang"]).size()})
  for i in 1,2,3: counts.reset_index(level=0, inplace=True)
  counts.rename(columns = {"source_x" : "source", "target_x" : "target"}, inplace=True)
  counts.sort_values(by = "count", inplace = True, ascending = False)
  def convert(x):
    x = x.replace("&apos;", "'").replace("&quot;", "\"")
    return x.decode("utf8")
  print(counts.to_html(index=False,formatters = {"source_x" : convert, "target_y" : convert}).encode("utf8"))

  print("</BODY>")

if __name__ == "__main__":
  main()
