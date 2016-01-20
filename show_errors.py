#!/usr/bin/env python
from __future__ import print_function

import cgi
import cgitb
import pandas

cgitb.enable()

LANGS = {
  "cs" : "Czech",
  "de" : "German", 
  "pl" : "Polish",
  "ro" : "Romanian"
}

def main():
  print("Content-Type: text/html")
  print()

  args = cgi.FieldStorage()
  if "lang" not in args or args["lang"].value not in LANGS:
    print("<h1>Error</h1>")
    print("Missing or unknown language id")
    print(args)
    return
  lang = args["lang"].value

  sentences = pandas.read_csv("sentences.csv")
  nodes = pandas.read_csv("nodes.csv")
  errors = nodes[(nodes.mt_label == "R")]
  errors = errors.merge(sentences, on=("sent_id", "annot_id"), suffixes=("_word", "_sentence"))
  errors.rename(columns={'lang_word':'lang'}, inplace=True)
  error_counts = pandas.DataFrame({"count" : errors.groupby(['source_word', 'target_word', 'lang']).size()})

  print("<head><meta charset=\"UTF-8\">")
  print("<TITLE>Common Errors: {}</TITLE>".format(LANGS[lang]))
  print("</head>")
  print("<BODY>")
  print("The table shows translations marked as <b>red</b> by any annotator<br>")

  error_counts = pandas.read_csv("error-counts.csv")
  def convert(x):
    x = x.replace("&apos;", "'").replace("&quot;", "\"")
    return x.decode("utf8")
  error_counts.sort_values(by="count", inplace=True, ascending=False)
  print(error_counts[error_counts.lang == lang].to_html(index=False,formatters = {"source_word" : convert, "target_word" : convert}).encode("utf8"))
  

  print("<BODY>")


if __name__ == "__main__":
  main()
