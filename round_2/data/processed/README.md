# Overview

This directory contains the annotation data, processed into two tables, stored in tsv format. The tables are:
* `nodes.tsv` Contains one entry for each node in each annotated sentence
* `sentences.tsv` Conatains one entry for each annotated sentence (note that the same sentence can be translated by several systems, and each translation could be annotated several times).

## Sentences
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
