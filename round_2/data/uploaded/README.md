## Overview
This directory contains the source, references, alignments and translation outputs used in the annotation.

## Data Sources
For en-cs, en-de and en-ro, the sentences are taken from the [WMT newstest2016 testset](http://www.statmt.org/wmt16/translation-task.html), selected to include 
both sentences with ranking evaluations, and sentence from medically-related articles. For en-pl, the 
sentences are from the [HimL test sets](http://www.himl.eu/test-sets).

## Systems
The following table shows the systems used in the comparison. Note that all systems are WMT16 news task submissions, except for en-pl.

|Pair | Name | Description |
|-----|------|------------ |
| en-cs | chimera | Charles University's Chimera system.  |
| en-cs | nmt | University of Edinburgh's NMT system.  |
| en-cs | tecto | Charles University's Tecto (deep syntactic) system. |
| en-de | nmt | University of Edinburgh's NMT system |
| en-de | pbmt | University of Edinburgh's PBMT system |
| en-de | syntax | University of Edinburgh's Syntax-based system |
| en-pl | nmt | NMT system built for HimL |
| en-pl | nmt | PBMT system built for HimL |
| en-ro | pbmt | University of Edinburgh's PBMT system  |
| en-ro | nmt | University of Edinburgh's NMT system  |
| en-ro | combo | QT21 system combination  |


## Files
Each subdirectory contains the following types of file:
* The source file (always English) is called `src.en`
* The reference file is called `ref.$LANG`
* The translation outputs are `$SYSTEM.$LANG`. There is a corresponding symlink for the source, `$SYSTEM.en`
* The alignments are in the "Moses" format (`$SYSTEM.align`) and the tool format (`$SYSTEM.ucca.align`). The alignments were created by forced aligning using a GIZA model.


