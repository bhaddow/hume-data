#!/usr/bin/env python

#
# Get the translations into the 4 himl languages, and their word alignments
#
import logging
import os
import subprocess
import sys

from collections import namedtuple


LOG = logging.getLogger(__name__)

SVN_REPO = "/home/bhaddow/work/himl/svn-repo/data"
NHS24_LENGTH = 1258
MOSES_SCRIPTS = "/home/bhaddow/moses.new/scripts"

def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

  # read references
  refs = {}
  for lang in "cs", "de", "ro", "pl":
    for domain in "nhs24", "cochrane":
      with open("%s/testset-processed/%s.testing.%s.sgm" % (SVN_REPO, domain, lang)) as ifh:
        refs[(lang,domain)] = []
        for line in ifh:
          if line.startswith("<seg"):
            start = line.find(">") + 1
            refs[(lang,domain)].append(line[start:-7])

  # Find out which lines we need

  ofhs = {lang :subprocess.Popen([MOSES_SCRIPTS + "/tokenizer/tokenizer.perl", "-a", "-l", lang], 
      stdout = open("data/texts/reference." + lang, "w"), stdin=subprocess.PIPE)  for lang in ("cs", "de", "ro", "pl")}
  sfh = open(SVN_REPO + "/ucca-humaneval-data/evaluation-data/himl.testing.en.selected.txt")
  for line in sfh:
    line_id,text = line[:-1].split(":",1)
    line_id = int(line_id)
    domain = "nhs24"
    if line_id >= NHS24_LENGTH:
      domain = "cochrane"
      line_id -= NHS24_LENGTH
    for lang,ofh in ofhs.iteritems():
      ofh.stdin.write(refs[(lang,domain)][line_id])
      ofh.stdin.write("\n")
      ofh.stdin.flush()
  #for ofh in ofhs.values():
  #   ofh.terminate()
      


if __name__ == "__main__":
  main()
