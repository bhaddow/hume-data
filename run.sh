python 
#!/usr/bin/bash
set -o xtrace

for file in ro1 ro2 pl1 pl2 cs1 de1
do
  python3 /Users/alexandrabirch/work/2015-himl-ucca/ucca-eval/analysis.py --inputFile /Users/alexandrabirch/work/2015-himl-ucca/ucca-eval/data/raw_15_11_26/new_mteval_$file\.dump

done
