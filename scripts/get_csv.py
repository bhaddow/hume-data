#!/usr/bin/env python3

#
# Create csv files with details of sentences and nodes
#

import argparse
import csv
import glob
import logging
import os
import os.path
import sys

from collections import Counter
from reader import get_sentences, ANNOTATION_KEY

LOG = logging.getLogger(__name__)

#
# Note: the source field in the ucca dump seems to be inconsistently normalised - sometimes it contains the "@-@", and
# somtimes not.
#
def deescape(line):
  return line.replace("@-@","-").replace("&quot;",'"').replace("&apos;", "'").replace("&amp;", "&").replace(" - ", "-").replace(" n't", "n 't")

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', nargs='+', dest='inFile', help="Input UCCAMT Eval dump files")
    parser.add_argument('-s', '--sentenceFile',   help="Sentence csv file", default="sentences.csv")
    parser.add_argument('-n', '--nodeFile',  help="Node csv file", default="nodes.csv")
    args = parser.parse_args()

    #Check timestamps before running update
    if args.inFile:
      inTime = 0
      for inFile in args.inFile:
        inFileTime = os.path.getmtime(inFile)
        if inFileTime > inTime:
          inTime = inFileTime
      #inTime is now the last modified dump. Is it older than the output files?
      if os.path.exists(args.sentenceFile) and os.path.getmtime(args.sentenceFile) > inTime and \
          os.path.exists(args.nodeFile) and  os.path.getmtime(args.nodeFile) > inTime:
        LOG.warn("Files {} and {} more recent than dumps, not recreating".format(args.nodeFile, args.sentenceFile))
        sys.exit(0)


    # Load references and bleu
    references = {}
    bleus = {}
    sources = []
    with open("data/texts/source.en") as sfh:
      sources = [deescape(line[:-1]) for line in sfh.readlines()]
    for lang in "cs", "de", "pl", "ro":
      with open("data/texts/reference." + lang) as rfh,\
        open("data/texts/bleu." + lang) as bfh:
        line_no = 0
        for rline,bline in zip(rfh,bfh):
          references[(lang,sources[line_no])] = (rline[:-1], float(bline[:-1]))
          line_no += 1

    inFile = args.inFile
    mt_keys = list(ANNOTATION_KEY.values()) + ["M"]
    mt_colkeys = ["mteval_{}".format(key) for key in mt_keys]
    with open(args.sentenceFile, "w") as csvfh,\
        open(args.nodeFile, "w") as ncsvfh:
      print("sent_id,annot_id,ucca_annot_id,lang,timestamp,source,target,reference,align,bleu,ucca_node_count,", file=csvfh, end="")
      print("ucca_H,", file=csvfh, end="")
      print(",".join(mt_colkeys), file=csvfh,end="")
      print(file=csvfh)

      print("node_id,sent_id,annot_id,lang,mt_label,child_count,children,parent,ucca_label,pos,source,target", file=ncsvfh)

      csv_writer = csv.writer(csvfh,  lineterminator=os.linesep)
      ncsv_writer = csv.writer(ncsvfh,  lineterminator=os.linesep)
      for sent in get_sentences(inFile):
        fields = []
        fields.append(sent.sent_id)
        fields.append(sent.annot_id)
        fields.append(sent.ucca_annot_id)
        fields.append(sent.lang)
        fields.append(sent.timestamp)
        fields.append(sent.source)
        fields.append(sent.target)
        ref,bleu = references[(sent.lang,deescape(sent.source))]
        fields.append(ref)
        fields.append(" ".join(["%s-%s" % (src,tgt) for src,tgt in sent.align]))
        fields.append(bleu)

        # ucca nodes and annotations
        target_tokens = sent.target.split()
        align_map = {src: target_tokens[tgt] for src,tgt in sent.align}
        mt_eval_counts = Counter()
        ucca_counts = Counter()
        for node in sent.ucca_tree.nodes:
          node = sent.ucca_tree.nodes[node]
          if node.tag != "FN": continue
          mt_annot = sent.mt_annotation.get(node.ID, "M")
          mt_eval_counts[mt_annot] += 1
          ucca_counts[node.ftag] += 1
          # Update the node file
          child_count = len(node.children)
          children = " ".join([child.ID for child in node.children])
          parent = "0"
          if node.fparent: parent = node.fparent.ID
          tag = node.ftag
          if not tag: tag = "root"
          pos,source,target = "-1","",""
          if node.children and node.children[0].tag == "Word":
            #print(node.ID, str(sent.sent_id), sent.annot_id)
            def get_src_tgt(child):
              if child.tag == "Word":
                return child.text, align_map.get(child.para_pos-1, "UNALIGNED"), str(child.para_pos-1)
              elif child.tag == "PNCT":
                return get_src_tgt(node.children[0])
            source,target,pos = [" ".join(l) for l in list(zip(*[get_src_tgt(node) for node in node.children]))]
          ncsv_writer.writerow((node.ID, str(sent.sent_id), sent.annot_id, sent.lang, mt_annot, \
                str(child_count), children, parent, tag, pos, source, target ))
        fields.append(sum(mt_eval_counts.values()))
        fields.append(ucca_counts["H"])
        fields += [mt_eval_counts[key] for key in mt_keys]

        csv_writer.writerow(fields)
 
if __name__ == "__main__":
  main()

