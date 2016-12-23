Brief description of file formats
=================================

sentences.csv
-------------

**description missing**

Sample:

```
sent_id,annot_id,ucca_annot_id,lang,timestamp,source,target,reference,align,bleu,ucca_node_count,ucca_H,mteval_A,mteval_B,mteval_O,mteval_R,mteval_G,mteval_M
505,cs1,lexi1,cs,2015-11-26 01:10:37.473793,"While many cases of angina can be treated with medication , a coronary angioplasty may be required to restore the blood supply to the heart in severe cases .","Mnoho případů , angina pectoris , může být léčeni s léky , koronární angioplastika může být potřebné k obnovení přívod krve do srdce v závažných případech .","I když většina případů anginy pectoris může být léčena léky , pro obnovení přívodu krve do srdce u závažných případů může být třeba koronární angioplastika .",1-0 2-1 4-3 4-4 5-6 6-7 7-8 8-9 9-10 10-11 12-12 13-13 14-14 15-15 16-16 17-17 18-18 19-19 21-19 20-20 22-21 23-21 24-22 25-23 26-24 27-25 28-26,0.148349,40,2,13,0,6,1,20,0
489,cs1,lexi1,cs,2015-11-26 01:03:19.216632,"Stopping this medication suddenly will lead to serious side effects , such as a rise in blood pressure or chest pain caused by reduction in oxygen to your heart muscle ( angina ) .","Zastavit léčbu náhle povede k závažné nežádoucí účinky , jako je zvýšení krevního tlaku nebo bolest na hrudi způsobené snížení kyslíku do srdečního svalu ( angina pectoris ) .",Náhlé vysazení tohoto léku vede k závažným nežádoucím účinkům jako je zvýšení krevního tlaku nebo bolest na hrudi způsobená sníženým přívodem kyslíku do srdečního svalu ( angina pectoris ) .,0-0 1-0 2-1 3-2 4-3 4-4 5-3 5-4 6-3 6-4 7-5 8-6 9-7 10-8 11-9 12-9 14-11 15-11 16-12 17-13 18-14 19-16 19-17 20-15 21-18 22-18 23-19 25-20 26-21 28-22 29-23 30-24 31-25 31-26 32-27 33-28,0.544368,47,1,14,1,8,1,16,7
```


nodes.csv
---------

Sample:

```
node_id,sent_id,annot_id,lang,mt_label,child_count,children,parent,ucca_label,pos,source,target
1.15,505,cs1,cs,O,1,0.9,1.14,R,8,with,s
1.41,505,cs1,cs,G,1,0.28,1.38,C,27,cases,případech
1.14,505,cs1,cs,A,2,1.15 1.16,1.3,A,-1,,
...
1.23,593,cs1,cs,G,3,0.13 0.15 1.24,1.22,C,12 14 12,amoxicillin clavulanate amoxicillin,amoxicilin klavulanová amoxicilin
```

Column meanings:
* **node_id** ... every UCCA node (a node in the source sentence annotation) has a unique node ID within a sentence, this is it.
* **sent_id** ... this is the sentence ID pointing hopefully to HimL test set
* **annot_id** ... this is the author of the HUME color labels of this sentence
* **lang** ... the target sentence where the annotated English was machine translated to
* **mt_label** ... this is the HUME "color" assigned to this node: Red, Orange, Green, Adequate, Bad
* **child_count** ... serves as a sanity check, the number of children of this UCCA node
* **children** ... space-delimited IDs of UCCA nodes that depend on the current node
* **parent** ... strictly speaking redundant, the ID of the parent of the current node
* **ucca_label** ... this is the UCCA label of the current node
* **pos** ... space-delimited indexes of source words in the source sentence that belong to this node
* **source** ... space-delimited source words that belong to this node
* **target** ... only indicative: target words that were automatically word-aligned to the source words of this node

What if a source word is not part of any UCCA node, we probably do not see such a word in the file at all.

In general, the full source sentence is relatively easy to reconstruct from
this (if all words belonged to an UCCA node), while the target sentences are
impossible to reconstruct and one should follow the
`sentences.csv`. Hopefully the tokenization agrees among the files.
