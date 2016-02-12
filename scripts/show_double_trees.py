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

def display(lang,sort):
  sentences = pandas.read_csv("sentences.csv")
  nodes = pandas.read_csv("nodes.csv", converters={'node_id': str, 'parent' : str})
  sentences = sentences[sentences.lang == lang]
  nodes = nodes[nodes.lang == lang]

  # Create table of matching nodes
  nodes = nodes.merge(nodes, on = ["node_id", "sent_id"])
  nodes = nodes[(nodes["annot_id_x"] < nodes["annot_id_y"])]
  nodes = nodes[(nodes["mt_label_x"] != "M") & (nodes["mt_label_y"] != "M")]
  nodes['match'] = nodes['mt_label_x'] == nodes['mt_label_y']

  # One record per sentence
  annot_id1,annot_id2 = sorted(sentences['annot_id'].unique())
  sentences = sentences[sentences.annot_id == annot_id1] #one record per sentence
  del sentences['mteval_A']
  del sentences['mteval_B']

  # Join match counts into sentence table
  grouped = nodes.groupby(['sent_id'], as_index=True)
  matches = pandas.DataFrame({ \
    'nodes' : grouped['match'].size(),
    'nodes_agree' : grouped['match'].sum(),
    'agreement' : grouped['match'].sum() / grouped['match'].size()
  })
  sentences = sentences.merge(matches, left_on="sent_id", right_index=True)
  sentences['nodes_agree'] = sentences['nodes_agree'].astype('int')

  # Source length
  sentences['src_length'] = sentences['source'].str.split().apply(len)
  
  # Columns should be sentence id, nodes, nodes agree, agreement , source length, bleu

  title = "All Doubly Annotated Trees: {}".format(LANGS[lang])
  print("<head><meta charset=\"UTF-8\">")
  print("<TITLE>{}</TITLE>".format(title))
  print("</head>")
  print("<BODY>")
  print("<h1>{}</h1>".format(title))
  print("<table border=1>")
  print("<tr>")
  headings = [("SentenceId", "sent_id"), ("Tree", ""),  ("Node count", "nodes"), ("Nodes agreeing", "nodes_agree"), \
      ("Agreement", "agreement"), ("Source length", "src_length"), ("Bleu", "bleu")]
  for h,sortorder in headings:
    if sortorder:
      print("<th><a href=\"show_double_trees.py?lang={}&sort={}\">{}</th>".format(lang,sortorder,h))
    else:
      print("<th>{}</th>".format(h))
  print("</tr>")

  for i,row in sentences.sort_values(by=sort, ascending=False).iterrows():
    fields = [row["sent_id"]]
    fields.append('<a href="show_double_tree.py?sent_id={}&annot_id1={}&annot_id2={}">tree</a>' \
          .format(row["sent_id"], annot_id1,annot_id2))
    fields += [row['nodes'], row['nodes_agree'], row['agreement'], row['src_length'], row['bleu']]
    print("<tr>")
    for f in fields:
      print("<th>{}</th>".format(f))
    print("</tr>")


  print("</table>")    
  print("</BODY>")
  print("</html>")

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

  sort = "sent_id"
  if "sort" in args:
    sort = args["sort"].value

  display(lang,sort)

if __name__ == "__main__":
  main()
  #display("ro", "agreement")
