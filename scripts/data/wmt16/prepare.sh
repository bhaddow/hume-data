moses_scripts=/Users/alexandrabirch/software/moses/mosesdecoder/scripts
lang=en
file=selected.source.en
tok_file=selected.source.tok.en
clean_tok_file=selected.source.clean.en

$moses_scripts/tokenizer/normalize-punctuation.perl -l $lang < $file | \
$moses_scripts/tokenizer/tokenizer.perl -a -l $lang  \
> $tok_file

#This file matches tokens in .tok.en but has no extra characters eg @-@ => -
perl clean_tok.pl < $tok_file > $clean_tok_file
