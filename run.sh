#!/bin/bash
set -o xtrace
DIR=/Users/alexandrabirch/work/2015-himl-ucca/ucca-eval

for file in de1
#for file in ro1 ro2 pl1 pl2 cs1 de1
do
  python3 $DIR/analysis.py --inputFile $DIR/data/raw_15_12_08/mteval_$file\.dump $DIR/data/raw_15_12_08/new_mteval_$file\.dump $DIR/data/raw_15_12_08/b2__mteval_$file\.dump $DIR/data/raw_15_12_08/b3__mteval_$file\.dump 
done
for file in ro1 ro2 pl1 cs1
do
  python3 $DIR/analysis.py --inputFile $DIR/data/raw_15_12_08/new_mteval_$file\.dump $DIR/data/raw_15_12_08/b2__mteval_$file\.dump $DIR/data/raw_15_12_08/b3__mteval_$file\.dump 

done
