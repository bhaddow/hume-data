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
  sentences['score'] = (sentences['mteval_A'] + sentences['mteval_G'] + sentences['mteval_O']/2) / \
                        (sentences['ucca_node_count'] - sentences['mteval_M'])
  sort = "sent_id"
  if "sort" in args:
    sort = args["sort"].value

  has_mult_annot = (lang == "ro" or lang == "pl")
  title = "All Annotated Trees: {}".format(LANGS[lang])

  print("<head><meta charset=\"UTF-8\">")
  print("<TITLE>{}</TITLE>".format(title))
  print("</head>")
  print("<BODY>")

  

  print("<h1>{}</h1>".format(title))
  print("<table border=1>")
  print("<tr>")
  headings = [("SentenceId", "sent_id")]
  if has_mult_annot:
    headings.append(("AnnotId", "annot_id"))
  headings += [("tree",""), ("bleu", "bleu"), ("Acceptable", "mteval_A") , ("Bad", "mteval_B"), ("Green", "mteval_G") \
    , ("Orange", "mteval_O"), ("Red", "mteval_R"), ("Missing", "mteval_M"), ("UCCA Score", "score")]
  for h,sortorder in headings:
    if sortorder:
      print("<th><a href=\"show_trees.py?lang={}&sort={}\">{}</th>".format(lang,sortorder,h))
    else:
      print("<th>{}</th>".format(h))
  print("</tr>")

  for i,row in sentences[sentences.lang == lang].sort_values(by=sort, ascending=False).iterrows():
    fields = [row["sent_id"]]
    if has_mult_annot:
      fields.append(row["annot_id"])
    fields.append('<a href="show_tree.py?sent_id={}&annot_id={}">tree</a>'.format(row["sent_id"], row["annot_id"]))
    fields += [row["bleu"], row["mteval_A"], row["mteval_B"], row["mteval_G"], row["mteval_O"], row["mteval_R"], row["mteval_M"], row["score"]]
    print("<tr>")
    for f in fields:
      print("<th>{}</th>".format(f))
    print("</tr>")

  print("</table>")    


  print("</BODY>")

if __name__ == "__main__":
  main()
