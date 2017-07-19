# hume-data

## Overview

This repository contains annotation data and scripts for the HUME (Human 
UCCA-based MT Evaluation) metric. 
This metric is based on the UCCA semantic representation and aims to measure
how much of the semantic content of the source is captured by the machine translation.

There were two rounds of annotation:
* `round_1` : This took place in 2015, and the results were published in 2016 at EMNLP
(see below). We annotated data from 4 language pairs (English to Czech, German, Polish and Romanian),
translated by a single MT system.
* `round_2` : This took place in 2016, using the same language pairs, but comparing different MT
systems, including phrase-based, syntax-based and neural.

The subdirectories `round_1` and `round_2` contain the raw data from the annotation tool, 
the data processed into a more accessible form (tsv) and the scripts for data processing and
analysis.

## References

The main reference for HUME is our EMNLP paper, which describes the round_1 annotation.

```
@inproceedings{birch2016emnlp,
  author = {{Alexandra Birch and Omri Abend and Ond\v{r}ej Bojar and Barry Haddow}},
  title = {HUME: Human UCCA-Based Evaluation of Machine Translation},
  booktitle = {Proceedings of EMNLP},
  year = {2016},
}
```

## Data Organisation

### Round 1
This is organised into the following directories:

* `round_1/data/uploaded` : The system outputs uploaded to the annotation tool, as well the sources, reference and  bleu scores. The source and references
are taken from the [HimL 2015 Test Sets](http://www.himl.eu/test-sets) 
* `round_1/data/raw-annotation` : The annotations dumped directly from the annotation tool.
* `round_1/data/processed` : The data from the tool, processed into more readable comma-separated value (csv) files.
* `round_1/data/direct-assessment` : The data gathered from direct assessment of the translation (i.e. adequacy judgements)

### Round 2
This is organised into the following directories


* `round_2/data/uploaded` : The data uploaded to the HUME annotation tool - sources, system outputs and alignments. Also the references. The data is taken from
the [HimL 2015 Test Sets](http://www.himl.eu/test-sets) and the [WMT16 News Test Sets](http://www.statmt.org/wmt16/translation-task.html)
* `round_2/data/raw-annotation` : The annotations dumped directly from the annotation tool.
* `round_2/data/processed` : The data from the tool, processed into more readable tab-separated value (tsv) files.

## Licence
The data sets are licensed under the [Creative Commons Attribution-NonCommercial 4.0 license](https://creativecommons.org/licenses/by-nc/4.0/),
and the source code is licensed under the [Apache Licencse 2.0](http://www.apache.org/licenses/LICENSE-2.0).

## Funding
This project has received funding from the European
Union’s Horizon 2020 research and innovation pro-
gramme under grant agreement 644402 (HimL).
