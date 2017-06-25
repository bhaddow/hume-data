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
import ucca
import pdb

from collections import Counter
from reader import get_sentences, parse_pairs, ANNOTATION_KEY

LOG = logging.getLogger(__name__)

#
# Note: the source field in the ucca dump seems to be inconsistently normalised - sometimes it contains the "@-@", and
# somtimes not.
#
def deescape(line):
  return line.replace("@-@","-").replace("&quot;",'"').replace("&apos;", "'").replace("&amp;", "&").replace(" - ", "-").replace(" n't", "n 't")


def compute_height(node):
  """
  Returns the height of node above the leaves.
  """
  if not isinstance(node,ucca.layer1.FoundationalNode):
    return 0
  return max([0] + [1+compute_height(ch) for ch in node.children]) 
 

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', nargs='+', dest='inFile', help="Input UCCAMT Eval dump files")
    parser.add_argument('-y', '--sysIndex', help = "System index file", default="../data/sys_index")
    parser.add_argument('-s', '--sentenceFile',   help="Sentence tsv file", default="sentences.tsv")
    parser.add_argument('-n', '--nodeFile',  help="Node tsv file", default="nodes.tsv")
    parser.add_argument("-c", "--comma-delimited", action="store_true")
    args = parser.parse_args()

    #Check timestamps before running update
    #if args.inFile:
    #  inTime = 0
    #  for inFile in args.inFile:
    #    inFileTime = os.path.getmtime(inFile)
    #    if inFileTime > inTime:
    #      inTime = inFileTime
    #  #inTime is now the last modified dump. Is it older than the output files?
    #  if os.path.exists(args.sentenceFile) and os.path.getmtime(args.sentenceFile) > inTime and \
    #      os.path.exists(args.nodeFile) and  os.path.getmtime(args.nodeFile) > inTime:
    #    LOG.warn("Files {} and {} more recent than dumps, not recreating".format(args.nodeFile, args.sentenceFile))
    #    sys.exit(0)


    # Load references and bleu
    references = {} #key: (lang,lineno)
    bleus = {} #key: (system,lang,lineno)
    aligns = {} #key: (system,lang,lineno)
    sources = {} #key: (lang,lineno)

    mypath = os.path.dirname(sys.argv[0])
    data_dir = mypath + "/../data/uploaded/"
    for lang in "cs", "de", "ro", "pl":
      with open("{0}/en-{1}/ref.{1}".format(data_dir, lang)) as rfh:
        for i,line in enumerate(rfh):
          references[(lang,i)] = line[:-1]
      bleu_files = glob.glob("{0}/en-{1}/*.{1}.bleu".format(data_dir,lang))
      for bleu_file in bleu_files:
        system = os.path.basename(bleu_file)[:-8]
        LOG.info("Loading bleu from {} for {}".format(bleu_file,  system))
        with open(bleu_file) as bfh:
          for i,line in enumerate(bfh):
            bleu = float(line[:-1])
            bleus[(system,lang,i)] = bleu
        
        #FIXME: Only need to load sources once
        with open(bleu_file[:-5]) as sfh:
          for i,line in enumerate(sfh):
            sources[(lang,i)] = line[:-1]

      align_files = glob.glob("{0}/en-{1}/*.ucca.align".format(data_dir,lang))
      for align_file in align_files:
        system = os.path.basename(align_file)[:-11]
        LOG.info("Loading align from {} for {}".format(align_file,  system))
        with open(align_file) as afh:
          for i,line in enumerate(afh):
            align = line[:-1]
            #print ("align, system, lang, i ", system, lang, i, align)
            aligns[(system,lang,i)] = align 


    # Load system index
    sys_index = {} # map user,sequence id to system
    with open(args.sysIndex) as sfh:
      for line in sfh:
        user,sequence_id,system = line[:-1].split()
        if user.startswith("user_"): user = user[5:]
        sys_index[(user, int(sequence_id))] = system


    inFile = args.inFile
    mt_keys = list(ANNOTATION_KEY.values()) + ["M"]
    mt_colkeys = ["mteval_{}".format(key) for key in mt_keys]
    with open(args.sentenceFile, "w") as csvfh,\
        open(args.nodeFile, "w") as ncsvfh:
      #print("sequence_id,sent_id,system_id,annot_id,ucca_annot_id,lang,timestamp,source,target,reference,align,bleu,ucca_node_count,", file=csvfh, end="")
      #print("ucca_H,", file=csvfh, end="")
      #print(",".join(mt_colkeys), file=csvfh,end="")
      #print(file=csvfh)

      #print("node_id,sequence_id,sent_id,system_id,annot_id,lang,mt_label,child_count,children,parent,ucca_label,pos,source,target,is_scene,height,num_tokens", file=ncsvfh)

      dialect = 'excel-tab'
      if args.comma_delimited:
        dialect = 'excel'
      csv_writer = csv.writer(csvfh,  lineterminator=os.linesep, dialect=dialect)
      ncsv_writer = csv.writer(ncsvfh,  lineterminator=os.linesep, dialect=dialect)
      sentence_fields = ["sequence_id","sent_id","system_id","annot_id","ucca_annot_id","lang","timestamp","source","target","reference","align","bleu","ucca_node_count"]
      sentence_fields.append("ucca_H")
      sentence_fields.extend(mt_colkeys)
      csv_writer.writerow(sentence_fields)
      ncsv_writer.writerow(["node_id","sequence_id","sent_id","system_id","annot_id","lang","mt_label","child_count","children","parent","ucca_label","pos","source","target","is_scene","height","num_tokens"])


      for sent in get_sentences(inFile):
        fields = []
        fields.append(sent.sequence_id)
        fields.append(sent.sent_id)
        system_id = sys_index[(sent.annot_id),int(sent.sequence_id)]
        #if (sent.annot_id,int(sent.sequence_id)) not in sys_index:
        #  print (sent.annot_id, int(sent.sequence_id), "NMT")
        #system_id = sys_index.get((sent.annot_id,int(sent.sequence_id)), "NMT")
        #print ("Sys", system_id, "annot", sent.annot_id, " seq", str(sent.sequence_id))
        fields.append(system_id)
        annot_id = sent.annot_id
        if annot_id == "de_sbmt_no_first100":
          annot_id = "de_all1"
        fields.append(annot_id)
        fields.append(sent.ucca_annot_id)
        fields.append(sent.lang)
        fields.append(sent.timestamp)
        fields.append(sent.source)
        fields.append(sent.target)
        #ref,bleu = references[(sent.lang,deescape(sent.source))]
        #FIXME
        #ref,bleu = "",0.0
        ref = references.get((sent.lang, int(sent.sent_id)), "")
        bleu = bleus.get((system_id.lower(), sent.lang, int(sent.sent_id)),0.0)
        if bleu == 0.0:
          LOG.info("Bleu missing. System: {}, Lang: {}, sentence: {}".format(system_id, sent.lang, sent.sent_id))
        fields.append(ref)
        align = aligns.get((system_id.lower(), sent.lang, int(sent.sent_id)),"")
        #print ("Align ", align)
        if align == "":
          LOG.info("Align missing. System: {}, Lang: {}, sentence: {}".format(system_id, sent.lang, sent.sent_id))
          if sent.lang != 'pl':
            pdb.set_trace()
        align_pairs = parse_pairs(align)
        fields.append(" ".join(["%s-%s" % (src,tgt) for src,tgt in align_pairs]))
        fields.append(bleu)
        
        # ucca nodes and annotations
        target_tokens = sent.target.split()
        align_map = {}
        for src,tgt in align_pairs:
          if tgt < len(target_tokens):
            align_map[src] = target_tokens[tgt]
          else:
            LOG.debug("Error in alignment: " + str(tgt))
        mt_eval_counts = Counter()
        ucca_counts = Counter()
        for node in sent.ucca_tree.nodes:
          node = sent.ucca_tree.nodes[node]
          if node.tag != "FN": continue
          is_scene = 'T' if node.is_scene() else 'F'
          
          mt_annot = sent.mt_annotation.get(node.ID, "M")
          mt_eval_counts[mt_annot] += 1
          ucca_counts[node.ftag] += 1
          # Update the node file
          child_count = len(node.children)
          children = " ".join([child.ID for child in node.children])
          parent = "0"
          if node.fparent: parent = node.fparent.ID
          tag = node.ftag
          tokens = list(node.get_terminals(punct=False))
          num_tokens = len(tokens)
          #if num_tokens == 1:
          #  print(tokens[0])
          #  print(ref)
          #  print(str(tokens[0]) in ref)
                      
          height = compute_height(node)
          
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
          ncsv_writer.writerow((node.ID, str(sent.sequence_id), str(sent.sent_id), system_id, annot_id, sent.lang, mt_annot, \
                str(child_count), children, parent, tag, pos, source, target, is_scene, str(height), str(num_tokens) ))
        fields.append(sum(mt_eval_counts.values()))
        fields.append(ucca_counts["H"])
        fields += [mt_eval_counts[key] for key in mt_keys]
        
        csv_writer.writerow(fields)

if __name__ == "__main__":
  main()

