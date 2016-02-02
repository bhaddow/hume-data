#!/usr/bin/env python
from __future__ import print_function

import cgi
import cgitb
import pandas

cgitb.enable()


def main():
  print("Content-Type: text/html")
  print()


  args = cgi.FieldStorage()
  if "sent_id" not in args  or "annot_id" not in args:
    print("<h1>Error</h1>")
    print("Missing sentence id or annotator id<br>")
    print(args)
    return

  annot_id = args["annot_id"].value
  sent_id = args["sent_id"].value

  print("<head><meta charset=\"UTF-8\">")
  print("<TITLE>Tree: {}, Annotator: {}</TITLE>".format(sent_id,annot_id))
  print("</head>")
  print("<BODY>")

  #print("<h2>Data</h2>")
  #print("<table border=1>")
  #def printrow(k,v):
  #  print("<tr><td>{}</td><td>{}</td></tr>".format(k,v))
  #printrow("SentenceId", sentence_id)
  #printrow("AnnotatorId", annot_id)
  #print("</table>")

  #print("<h2>Tree</h2>")
  print('<img src="trees/tree_{}_{}.png" width="2000">'.format(sent_id,annot_id))

  print("</BODY>")

if __name__ == "__main__":
  main()

