# Overview

This directory contains the annotation data, processed into two tables, stored in tsv format. The tables are:
* `nodes.tsv` Contains one entry for each node in each annotated sentence
* `sentences.tsv` Contains one entry for each annotated sentence (note that the same sentence can be translated by several systems, and each translation could be annotated several times).

## Sentences
Sample:

```
200	300	NMT	de_all1	amittaic	de	2017-04-10 13:12:38.086646	Obviously this is subject to you being a decent baker .	Das ist natürlich für Sie ein anständiger Bäcker .	Natürlich hängt dies davon ab , ob Sie ein anständiger Bäcker sind .	1-0 2-1 0-2 4-3 5-4 7-5 6-6 8-6 9-7 10-8	0.263611	15	1	2	3	0	3	7	0
149	249	NMT	de_all1	amittaic	de	2017-04-10 13:12:27.884610	The US economy has been performing relatively well , the recovery adding trillions of dollars to the balance sheet and generating little inflation .	Die US - Wirtschaft hat relativ gut funktioniert , die Erholung hat Billionen Dollar in die Bilanz gezogen und wenig Inflation erzeugt .	Die US @-@ Wirtschaft ist auf einem relativ guten Leistungsstand , Billionen Dollar werden zur Bilanz hinzugefügt und generieren nur eine geringe Inflation .	0-0 1-1 1-2 2-3 3-4 6-5 7-6 8-8 9-9 10-10 11-12 12-12 13-12 14-13 15-14 16-15 17-16 18-16 20-17 19-18 21-19 22-20 23-22	0.104363	32	3	10	0	4	0	18	0
199	299	NMT	de_all1	amittaic	de	2017-04-10 13:07:15.104220	Make friends through baking .	Machen Sie Freunde durch Backen .	Freundschaft schließen durch Backen .	0-0 1-2 2-3 3-4 4-5	0.411134	8	1	4	0	0	1	3	0
198	298	NMT	de_all1	amittaic	de	2017-04-10 13:06:26.910057	He saw some things .	Er hat einige Dinge gesehen .	Er sah einige Dinge .	0-0 1-1 1-4 2-2 3-3 4-5	0.330316	7	1	3	0	0	0	4	0
```

These are the columns of the sentences table:

* `sequence_id`     : The id assigned to this annotation by the tool.
* `sent_id`         : The id of the sentence, indicating its position in the uploaded corpus.
* `system_id`       : The id of the MT system used to generate the  translation.
* `annot_id`        : Identifies the HUME annotator.
* `ucca_annot_id`   : Identifies the UCCA annotator.  
* `lang`            : The language of the target sentence.
* `timestamp`       : Completion time of the annotation.
* `source`          : Source sentence (always English and tokenised).
* `target`          : MT output (tokenised).
* `reference`       : Reference sentence (tokenised).
* `align`           : Alignment between source and target.
* `bleu`            : Sentence bleu of target w.r.t reference.
* `ucca_node_count` : Number of UCCA nodes in sentence.
* `ucca_H`          : Number of UCCA H nodes.
* `mteval_A`        : Number of structural nodes annotated as A (Acceptable)
* `mteval_B`        : Number of structural nodes annotated as B (Bad)
* `mteval_O`        : Number of lexical nodes annotated as O (Orange - partially correct)
* `mteval_R`        : Number of lexical nodes annotated as R (Red - incorrect)
* `mteval_G`        : Number of lexical nodes annotated as G (Green - correct)
* `mteval_M`        : Number of UCCA nodes with no annotation (Missing)

## Nodes
Sample:

```
1.1	200	300	NMT	de_all1	de	A	2	1.2 1.16	0	root	-1			F	5	10	Linkage	Root
1.10	200	300	NMT	de_all1	de	G	1	0.6	1.9	A	5	you	Sie	F	1	1	Other	Scene
1.11	200	300	NMT	de_all1	de	R	1	0.7	1.9	S	6	being	anständiger	F	1	1	Other	Scene
1.12	200	300	NMT	de_all1	de	A	3	1.13 1.14 1.15	1.9	A	-1			F	2	3	Elaboration	Scene
1.13	200	300	NMT	de_all1	de	G	1	0.8	1.12	E	7	a	ein	F	1	1	Other	Elaboration
1.14	200	300	NMT	de_all1	de	G	1	0.9	1.12	E	8	decent	anständiger	F	1	1	Other	Elaboration
1.15	200	300	NMT	de_all1	de	G	1	0.10	1.12	C	9	baker	Bäcker	F	1	1	Other	Elaboration
```

These are the columns of the nodes table:

* `node_id`       : The id given by the UCCA tool.
* `sequence_id`   : As in sentences.tsv
* `sent_id`       : As in sentences.tsv
* `system_id`     : As in sentences.tsv
* `annot_id`      : As in sentences.tsv
* `lang`          : As in sentences.tsv
* `mt_label`      : The HUME label (A, B, R, G, O) or M (missing)
* `child_count`   : The number of children this node has
* `children`      : The children of this node (list of node_ids)
* `parent`        : The parent of this node (or 0 for root node)
* `ucca_label`    : The UCCA label of this node
* `pos`           : The position of the node in the source (Set to -1 for a structural node)
* `source`        : The source span of the node (Missing for structural nodes)
* `target`        : The target span. This is computed by projecting through the alignment, so can be "UNALIGNED".
* `is_scene`      : Whether the node is an UCCA scene.
* `height`        : The height of the node in the UCCA tree.
* `num_tokens`    : The number of tokens spanned by the node.
* `ucca_construction_type`  : The coarse UCCA category
* `parent_ucca_construction_type`  : The parent's coarse UCCA category
