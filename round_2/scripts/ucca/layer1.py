"""Describes the foundational level elements (layer 1) of the UCCA annotation.

Layer 1 is the foundational layer of UCCA, whose Nodes and Edges represent
scene objects and relations. The basic building blocks of this layer are
the FNode, which is a participant in a scene relation (including the
relation itself), and the various Edges between these Nodes, which represent
the type of relation between the Nodes.

"""

import operator

from ucca import core, layer0


# Layer ID
LAYER_ID = '1'


class NodeTags:
    """Layer 1 Node tags."""
    Foundational = 'FN'
    Linkage = 'LKG'
    Punctuation = 'PNCT'
    __init__ = None


class EdgeTags:
    """Layer 1 Edge tags."""
    ParallelScene = 'H'
    Time = 'Ti'
    Participant = 'A'
    Process = 'P'
    State = 'S'
    Adverbial = 'D'
    Ground = 'G'
    Center = 'C'
    Elaborator = 'E'
    Function = 'F'
    Connector = 'N'
    Relator = 'R'
    Linker = 'L'
    Punctuation = 'U'
    Terminal = 'T'
    LinkRelation = 'LR'
    LinkArgument = 'LA'
    __init__ = None


# Attribute entries
ATTRIB_KEYS = ('remote', 'implicit', 'uncertain', 'suggest')


class MissingRelationError(core.UCCAError):
    """Exception raised when a required edge is not present."""
    pass


def _single_child_by_tag(node, tag, must=True):
    """Returns the Node which is connected with an Edge with the given tag.

    Assumes that there is only one Node connected with an Edge with this tag.

    Args:
        node: the Node which is the parent of the Edge (and returned Node).
        tag: the tag of the Edge to look for.
        must: if set to True (default), if no Node is found, raise an
            exception. Otherwise, returns None if not found.

    Returns:
        The connected Node, or None if not found

    Raises:
        MissingRelationError if Node not found and must is set to True

    """
    for edge in list(node):
        if edge.tag == tag:
            return edge.child
    if must:
        raise MissingRelationError()
    else:
        return None


def _multiple_children_by_tag(node, tag):
    """Returns the Nodes which are connected with an Edge with the given tag.

    Args:
        node: the Node which is the parent of the Edge (and returned Nodes).
        tag: the tag of the Edges to look for.

    Returns:
        A list of connected Nodes, can be empty

    """
    return [edge.child for edge in list(node) if edge.tag == tag]


class PunctNode(core.Node):
    """Encapsulates punctuation :class:layer0.Terminal objects.

    Attributes:
        terminals: return the :class:layer0.Terminal objects encapsulated
            by this Node in a list (at least one, usually not more than 1).
        start_position:
        end_position:
            start/end position of the first/last terminal in the span of
            the PunctNode.

    """

    @property
    def terminals(self):
        return self.children

    @property
    def start_position(self):
        return self.children[0].position

    @property
    def end_position(self):
        return self.children[-1].position

    def __str__(self):
        return ' '.join(str(x) for x in self.terminals)


class Linkage(core.Node):
    """A Linkage between parallel scenes.

    A Linkage object represents a connection between two parallel scenes.
    The semantic type of the link is not determined in this object, but the
    :class:FoundationalNode of linkage is referred as the link relation,
    and the linked scenes are referred to as the arguments.

    Most cases will have two arguments, but some constructions have 1 or 3+
    arguments, depending on the semantic connection.

    Attributes:
        relation: FoundationalNode of the relation words.
        arguments: list of FoundationalNodes of the relation participants.

    """

    @property
    def relation(self):
        return _single_child_by_tag(self, EdgeTags.LinkRelation)

    @property
    def arguments(self):
        return _multiple_children_by_tag(self, EdgeTags.LinkArgument)

    def __str__(self):
        return "{}-->{}".format(str(self.relation.ID),
                                ','.join(x.ID for x in self.arguments))


class FoundationalNode(core.Node):
    """The basic building block of UCCA annotation, represents semantic units.

    Each FoundationalNode (FNode for short) represents a semantic unit in the
    text, with relations to other semantic units. In essence, the FNodes form
    a tree of annotation, when remote units are ignored. This means that each
    FNode has exactly one FNode parent, and for completeness, there is also
    a "Passage Head" FNode which is the FNode parent of all parallel scenes and
    linkers in the top-level of the annotation.

    Remote units are FNodes which are shared between two or more different
    FNodes, and hence have two FNode parents (participate in two relations).
    In such cases there is only one FNode parent, as the other Edges to parents
    are marked with the 'remote' attribute (set to True).

    Implicit Nodes are ones which aren't mentioned in the text, and hence
    doesn't have any Terminal units in their span. In such cases, they will
    have an 'implicit' attribute set to True, and will take the position -1
    (both start and end positions).

    Attributes:
        participants:
        adverbials:
        grounds:
        elaborators:
        centers:
        linkers:
        parallel_scenes:
        functions:
        punctuation:
        terminals:
            a list of all FNodes under self whose edge tag is one of
            these types.
        process:
        state:
        connector:
        relator:
            Returns the FNode under self whose edge tag is one of these types,
            or None in case it isn't found.
        start_position:
        end_position:
            start/end position of the first/last terminal in the span of
            the FNode, without counting in remote FNodes. If the FNode is
            implicit or have no Terminals for some reason, returns -1 (both).
        fparent: the FNode parent (FNode with incoming Edge, not remote) of
            this FNode. There is exactly one for each FNode except the Passage
            head, which returns None.
        ftag: the tag of the Edge connecting the fparent (as described above)
            with this FNode
        discontiguous: whether this FNode has continuous Terminals or not

    """

    @property
    def participants(self):
        return _multiple_children_by_tag(self, EdgeTags.Participant)

    @property
    def adverbials(self):
        return _multiple_children_by_tag(self, EdgeTags.Adverbial)

    @property
    def grounds(self):
        return _multiple_children_by_tag(self, EdgeTags.Ground)

    @property
    def centers(self):
        return _multiple_children_by_tag(self, EdgeTags.Center)

    @property
    def elaborators(self):
        return _multiple_children_by_tag(self, EdgeTags.Elaborator)

    @property
    def linkers(self):
        return _multiple_children_by_tag(self, EdgeTags.Linker)

    @property
    def parallel_scenes(self):
        return _multiple_children_by_tag(self, EdgeTags.ParallelScene)

    @property
    def functions(self):
        return _multiple_children_by_tag(self, EdgeTags.Function)

    @property
    def punctuation(self):
        return _multiple_children_by_tag(self, EdgeTags.Punctuation)

    @property
    def terminals(self):
        return _multiple_children_by_tag(self, EdgeTags.Terminal)

    @property
    def process(self):
        return _single_child_by_tag(self, EdgeTags.Process, False)

    @property
    def state(self):
        return _single_child_by_tag(self, EdgeTags.State, False)

    @property
    def connector(self):
        return _single_child_by_tag(self, EdgeTags.Connector, False)

    @property
    def relator(self):
        return _single_child_by_tag(self, EdgeTags.Relator, False)

    def _fedge(self):
        """Returns the Edge of the fparent, or None."""
        for edge in self.incoming:
            if (edge.parent.layer.ID == LAYER_ID and
                    edge.parent.tag == NodeTags.Foundational and
                    not edge.attrib.get('remote')):
                return edge
        return None

    @property
    def fparent(self):
        edge = self._fedge()
        return edge.parent if edge else None

    @property
    def ftag(self):
        edge = self._fedge()
        return edge.tag if edge else None

    def get_terminals(self, punct=True, remotes=False):
        """Returns a list of all terminals under the span of this FNode.

        Args:
            punct: whether to include punctuation Terminals, defaults to True
            remotes: whether to include Terminals from remote FNodes, defaults
                to false

        Returns:
            a list of :class:layer0.Terminal objects

        """
        terms = []
        for edge in list(self):
            if ((edge.attrib.get('remote', False) and not remotes) or
                    (edge.tag == EdgeTags.Punctuation and not punct)):
                continue
            elif edge.tag == EdgeTags.Terminal:
                terms.append(edge.child)
            elif edge.tag == EdgeTags.Punctuation:
                terms.extend(edge.child.terminals)
            else:
                terms.extend(edge.child.get_terminals(punct, remotes))
        terms.sort(key=operator.attrgetter('position'))
        return terms

    @property
    def start_position(self):
        try:
            return self.get_terminals()[0].position
        except IndexError:  # implicit unit or having no Terminals
            return -1

    @property
    def end_position(self):
        try:
            return self.get_terminals()[-1].position
        except IndexError:  # implicit unit or having no Terminals
            return -1

    @property
    def discontiguous(self):
        terms = self.get_terminals()
        return any(terms[i].position + 1 != terms[i + 1].position
                   for i in range(len(terms) - 1))

    def get_sequences(self):
        if self.attrib.get('implicit'):
            return []
        pos = sorted([x.position for x in self.get_terminals()])

        # all terminals which end a sequence, including the last one
        seq_closers = [pos[i] for i in range(len(pos) - 1)
                       if pos[i] + 1 < pos[i + 1]] + [pos[-1]]

        # all terminals which start a sequence, including the first one
        seq_openers = [pos[0]] + [pos[i] for i in range(1, len(pos))
                                  if pos[i - 1] < pos[i] - 1]
        return [(op, cl) for op, cl in zip(seq_openers, seq_closers)]

    def to_text(self):
        """Returns the text in the span of self, separated by spaces."""
        return ' '.join(t.text for t in self.get_terminals())

    def is_scene(self):
        return (self.state is not None or self.process is not None)

    def str_sequences(self):
        """Returns a list of stringified sequences and positions of this FNode.

        For continuous FNodes, it will return a 1-item list. The format
        of the chunks is as follows:
            Terminals: just the text of it
            Punctuation: just the text of the terminal(s) under it
            FNodes: According to their str()

        """
        if not self.discontiguous:
            return [(str(self), self.start_position, self.end_position)]
        for start, end in self.get_sequences():
            pass

    def __str__(self):
        start = lambda x: (x.position if x.layer.ID == layer0.LAYER_ID else
                           x.start_position)
        end = lambda x: (x.position if x.layer.ID == layer0.LAYER_ID else
                         x.end_position)
        sorted_edges = sorted(list(self), key=lambda edge: start(edge.child))
        output = ''
        for i, edge in enumerate(sorted_edges):
            node = edge.child
            if edge.tag == EdgeTags.Terminal:
                space = ' ' if not end(node) == self.end_position else ''
                output += '{}{}'.format(str(node), space)
            else:
                edge_tag = edge.tag
                if edge.attrib.get('remote'):
                    edge_tag = edge_tag + '*'
                if edge.attrib.get('uncertain'):
                    edge_tag = edge_tag + '?'
                if start(node) == -1:
                    output += "[{} IMPLICIT] ".format(edge_tag)
                else:
                    output += "[{} {}] ".format(edge_tag, str(node))
            if (start(node) != -1 and not edge.attrib.get('remote')
                    and i + 1 < len(sorted_edges)
                    and end(node) + 1 < start(sorted_edges[i + 1].child)):
                output += "... "  # adding '...' if discontiguous
        return output

    def get_top_scene(self):
        """Returns the top-level scene this FNode is within, or None"""
        if self in self.layer.top_scenes:
            return self
        elif self.fparent is None:
            return None
        else:
            return self.fparent.get_top_scene()


class Layer1(core.Layer):
    """

    """

    def __init__(self, root, attrib=None, *, orderkey=core.id_orderkey):
        super().__init__(ID=LAYER_ID, root=root, attrib=attrib,
                         orderkey=orderkey)
        self._scenes = []
        self._linkages = []
        self._head_fnode = FoundationalNode(root=root,
                                            tag=NodeTags.Foundational,
                                            ID=self.next_id())
        self._all = [self._head_fnode]
        self._heads = [self._head_fnode]

    @property
    def top_scenes(self):
        return self._scenes[:]

    @property
    def top_linkages(self):
        return self._linkages[:]

    def next_id(self):
        """Returns the next avilable ID string for this layer."""
        n = len(self._all) + 1
        while True:
            ID = "{}{}{}".format(LAYER_ID, core.Node.ID_SEPARATOR, n)
            if ID not in self._all:
                return ID
            else:
                n = n + 1

    def add_fnode(self, parent, edge_tag, *, implicit=False):
        """Adds a new :class:FNode whose parent and Edge tag are given.

        Args:
            parent: the FNode which will be the parent of the new FNode.
                If the parent is None, adds under the layer head FNode.
            edge_tag: the tag on the Edge between the parent and the new FNode.
            implicit: whether to set the new FNode as implicit (default False)

        Returns:
            the newly created FNode

        Raises:
            core.FrozenPassageError if the Passage is frozen

        """
        if parent is None:
            parent = self._head_fnode
        node_attrib = {'implicit': True} if implicit else {}
        fnode = FoundationalNode(root=self.root, tag=NodeTags.Foundational,
                                 ID=self.next_id(), attrib=node_attrib)
        parent.add(edge_tag, fnode)
        return fnode

    def add_remote(self, parent, edge_tag, child):
        """Adds a new :class:core.Edge with remote attribute between the nodes.

        Args:
            parent: the parent of the remote Edge
            edge_tag: tag of the Edge
            child: the child of the remote Edge

        Raises:
            core.FrozenPassageError if the Passage is frozen

        """
        parent.add(edge_tag, child, edge_attrib={'remote': True})

    def add_punct(self, parent, terminal):
        """Adds a PunctNode as the child of parent and the Terminal under it.

        Args:
            parent: the parent of the newly created PunctNode. If None, adds
                under rhe layer head FNode.
            terminal: the punctuation Terminal we want to put under parent.

        Returns:
            the newly create PunctNode.

        Raises:
            core.FrozenPassageError if the Passage is frozen.

        """
        if parent is None:
            parent = self._head_fnode
        punct_node = PunctNode(root=self.root, tag=NodeTags.Punctuation,
                               ID=self.next_id())
        parent.add(EdgeTags.Punctuation, punct_node)
        punct_node.add(EdgeTags.Terminal, terminal)
        return punct_node

    def add_linkage(self, relation, *args):
        """Adds a Linkage between the link relation and the linked arguments.

        Linkage objects are all heads and have no parents.

        Args:
            relation: the link relation FNode.
            args: any number (at least 1) of linkage arguments FNodes.

        Returns:
            the newly created Linkage

        Raises:
            core.FrozenPassageError if the Passage is frozen.

        """
        linkage = Linkage(root=self.root, tag=NodeTags.Linkage,
                          ID=self.next_id())
        linkage.add(EdgeTags.LinkRelation, relation)
        for arg in args:
            linkage.add(EdgeTags.LinkArgument, arg)
        return linkage

    def _check_top_scene(self, node):
        """Checks whether a node is a scene, and a top-level one.

        A top level scene is one which is not embedded in any other scene.

        Args:
            node: the FNode to check.

        Returns:
            True iff node is a top-level scenes.

        """
        if not node.is_scene():
            return False
        while node.fparent not in (None, self._head_fnode):
            node = node.fparent
            if node.is_scene():
                return False
        return True

    def _update_top_scene(self, node):
        """Adds/removes the node if it's a top-level scene."""
        if node.tag != NodeTags.Foundational:
            return
        if node in self._scenes and not self._check_top_scene(node):
            self._scenes.remove(node)
        elif node not in self._scenes and self._check_top_scene(node):
            self._scenes.append(node)
            # Other scenes may now become not top-level, check it
            for ts in self._scenes[:-1]:
                if not self._check_top_scene(ts):
                    self._scenes.remove(ts)
            self._scenes.sort(key=self.orderkey)

    def _update_top_linkage(self, linkage):
        """Adds/removes the linkage if it's a top level linkage."""
        if all(fnode in self._scenes for fnode in linkage.arguments):
            if linkage not in self._linkages:
                self._linkages.append(linkage)
                self._linkages.sort(key=self.orderkey)
        elif linkage in self._linkages:
            self._linkages.remove(linkage)

    def _update_edge(self, edge):
        """Adds the Edge to the Layer, and updates top scenes and linkers."""
        self._update_top_scene(edge.parent)
        self._update_top_scene(edge.child)
        for lkg in [x for x in edge.parent.parents
                    if x.tag == NodeTags.Linkage]:
            self._update_top_linkage(lkg)
        for lkg in [x for x in edge.child.parents
                    if x.tag == NodeTags.Linkage]:
            self._update_top_linkage(lkg)

    def _add_edge(self, edge):
        super()._add_edge(edge)
        self._update_edge(edge)

    def _remove_edge(self, edge):
        super()._remove_edge(edge)
        self._update_edge(edge)

    def _change_edge_tag(self, edge, old_tag):
        super()._change_edge_tag(edge, old_tag)
        self._update_edge(edge)
