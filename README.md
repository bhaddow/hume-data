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

The main reference for HUME is our EMNLP paper

```
@inproceedings{birch2016emnlp,
  author = {{Alexandra Birch and Omri Abend and Ond\v{r}ej Bojar and Barry Haddow}},
  title = {HUME: Human UCCA-Based Evaluation of Machine Translation},
  booktitle = {Proceedings of EMNLP},
  year = {2016},
}
```

## Licence
The data sets are licensed under the [Creative Commons Attribution-NonCommercial 4.0 license](https://creativecommons.org/licenses/by-nc/4.0/),
and the source code is licensed under the [Apache Licencse 2.0](http://www.apache.org/licenses/LICENSE-2.0).

## Funding
This project has received funding from the European
Union’s Horizon 2020 research and innovation pro-
gramme under grant agreement 644402 (HimL).
