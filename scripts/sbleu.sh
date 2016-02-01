#!/bin/sh

for l in cs de pl ro; do
  ~/moses.new/bin/sentence-bleu data/texts/reference.$l < data/texts/system.$l > data/texts/bleu.$l
done
