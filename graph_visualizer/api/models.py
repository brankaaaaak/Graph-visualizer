import copy
from django.db import models
"""
Data structures used to represent the graph model.

Contains:
- Node: a graph node with attributes and edges
- Edge: a connection between two nodes with a relation
- Graph: collection of nodes and algorithms
- TreeNode / Tree: hierarchical structure for tree view
"""
class Node:
    """
    Represents a node in the graph.

    Attributes:
        id (Any): Unique identifier.
        attributes (dict): Key-value attributes of the node.
        edges (List[Edge]): Outgoing edges from the node.
    """
    def __init__(self, id):
        self._id = id
        self._edges = []
        self._attributes = {}

    @property
    def edges(self):
        return self._edges

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def attributes(self):
        return self._attributes

    @edges.setter
    def edges(self, value):
        self._edges = value

    @attributes.setter
    def attributes(self, value):
        self._attributes = value

    def __hash__(self):
        return hash(self._id)

    def degree(self):
        return len(self._edges)

    def __eq__(self, value):
        if not isinstance(value, Node):
            return False
        return self._id == value._id

    def has_edge(self, edge):
        for e in self._edges:
            if e == edge:
                return e
        return None

    def add_edge(self, edge):
        is_present = self.has_edge(edge)
        if is_present:
            self._edges[self._edges.index(is_present)] = edge
        else:
            self._edges.append(edge)

    def remove_edge_to(self, target_node, relation):
        for edge in self._edges:
            if edge.target == target_node and edge.relation == relation:
                self._edges.remove(edge)
                return edge
        return None

    def get_attributes(self):
        return self._attributes
    def add_attribute(self, key, value):
        self._attributes[key] = value

    def is_related(self, node):
        return any(
            (edge.origin == self and edge.target == node) or
            (edge.target == self and edge.origin == node)
            for edge in self.edges
        )

    def get_relations(self):
        return list({edge.relation for edge in self.edges})

    def get_related_nodes(self, relation):
        return [edge.target for edge in self.edges if edge.relation == relation and edge.origin == self]


class Edge:
    """
    Represents an edge between two nodes.

    Attributes:
        origin (Node): Source node.
        target (Node): Destination node.
        relation (str): Relation name or label.
        weight (float): Weight of the edge.
        directed (bool): Whether the edge is directed.
    """
    def __init__(self, origin, target, relation, weight, directed):
        self._origin = origin
        self._target = target
        self._relation = relation
        self._weight = weight
        self._directed = directed
    @property
    def weight(self):
        return self._weight

    @property
    def relation(self):
        return self._relation
    @relation.setter
    def relation(self, value):
        self._relation = value

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = value

    @property
    def is_directed(self):
        return self._directed
    @property
    def weight(self):
        return self._weight
    def __hash__(self):
        return hash((self._origin,self._target))

    def __str__(self):
        return f'({self._origin}, {self._target}, {self._relation}, {self._weight}, {self._directed})'

    def __eq__(self, other) -> bool:
        if self._relation != other.relation:
            return False
        elif self._weight != other.weight:
            return False
        elif self._directed != other._directed:
            return False
        elif self._target != other.target:
            return False
        return True

    def get_nodes(self):
        return self._origin, self._target

class Graph:
    """
    Represents a graph structure.

    Attributes:
        nodes (List[Node]): List of all nodes in the graph.
        directed (bool): Whether the graph is directed.
    """
    def __init__(self):
        self._nodes = []
        self._visited_nodes = []
        self._path = []
        self._nodes_to_contour = []

    @property
    def nodes(self):
        return self._nodes
    @nodes.setter
    def nodes(self, value):
        self._nodes = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def visited_nodes(self):
        return self._visited_nodes
    @visited_nodes.setter
    def visited_nodes(self, value):
        self._visited_nodes = value

    def node_degree(self, node):
        return node.degree()

    def get_edges(self):
        edges = set()
        for node in self._nodes:
            edges.update(node.edges)
        return edges
    def get_nodes(self):
        return self._nodes
    def get_number_of_nodes(self):
        return len(self._nodes)

    def get_number_of_edges(self):
        directed = sum(1 for edge in self.get_edges() if edge._directed())
        undirected = len(self.get_edges()) - directed
        return directed + undirected // 2

    def is_directed(self):
        edges = self.get_edges()
        if edges:
            first_edge = list(edges)[0]
            return first_edge._directed
        return False

    def has_node(self, n):
        for node in self.nodes:
            if n == node:
                return node
        return None

    def get_node(self, id):
        return next((node for node in self.nodes if str(node.id) == str(id)), None)

    def get_edge(self, source_id, target_id):
        for node in self._nodes:
            if str(node.id) == str(source_id):
                for edge in self.get_edges():
                    if str(edge.origin.id) == str(source_id) and str(edge.target.id) == str(target_id):
                        return edge
                    if not self.is_directed():
                        if str(edge.origin.id) == str(target_id) and str(edge.target.id) == str(source_id):
                            return edge
        return None

    def insert_node(self, node):
        existing_node = self.has_node(node)
        if existing_node:
            self._nodes[self._nodes.index(existing_node)] = node
        else:
            self._nodes.append(node)

    def insert_edge(self, edge: Edge):
        edge.origin.add_edge(edge)

        if not edge._directed:
            edge.target.add_edge(edge)

    def remove_edge(self, origin_id, target_id, relation):

        origin_node = self.get_node(origin_id)
        target_node = self.get_node(target_id)

        if not origin_node or not target_node:
            return False

        edge_to_remove = None
        for edge in origin_node.edges:
            if edge.target == target_node and edge.relation == relation:
                edge_to_remove = edge
                break

        if not edge_to_remove:
            return False

        origin_node.edges.remove(edge_to_remove)

        if not edge_to_remove.is_directed:
            for edge in target_node.edges:
                if edge.target == origin_node and edge.relation == relation:
                    target_node.edges.remove(edge)
                    break
        return True

    def find_subgraphs(self, nodes=None, graphs=None):
        """
        Splits the graph into subgraphs (connected components).
        """
        if not nodes:
            nodes = []
        if not graphs:
            graphs = []
        changes = True
        if not nodes:
            nodes = list(self._nodes)

        connected = {}
        for node in nodes:
            connected[node] = False
        if nodes:
            connected[nodes[0]] = True

        if list(connected.values()) == [True * len(nodes)]:
            subgraph = Graph()
            subgraph.nodes = list(connected.keys())
            graphs.append(subgraph)
            return graphs

        while changes:
            changes = False
            for node in nodes:
                if connected[node]:
                    if self.check_as_true(node.edges, connected):
                        changes = True
                else:
                    if self.check_if_true(node, connected):
                        connected[node] = True
                        if self.check_as_true(node.edges, connected):
                            changes = True

        if list(connected.values()) == [True for _ in range(len(connected.values()))]:
            subgraph = Graph()
            subgraph.nodes = list(connected.keys())
            graphs.append(subgraph)
            return graphs

        removed = self.remove_connected_nodes(nodes, connected)
        subgraph = Graph()
        subgraph.nodes = removed
        graphs.append(subgraph)
        return self.find_subgraphs(nodes, graphs)

    def check_if_true(self, node, connected):
        for edge in node.edges:
            try:
                if connected[edge.origin]:
                    return True
                elif connected[edge.target]:
                    return True
            except KeyError:
                pass
        return False

    def remove_node(self, node_to_remove):
        if node_to_remove in self.nodes:
            self._nodes.remove(node_to_remove)
            return True
        return False

    def update_node(self, node, key, value):
        if node in self.nodes:
            node.add_attribute(key, value)
            return True
        return False

    def check_as_true(self, edges, connected):
        changes = False
        for edge in edges:
            if edge.origin not in connected or edge.target not in connected:
                continue
            if connected[edge.origin] is False:
                changes = True
            elif connected[edge.target] is False:
                changes = True
            connected[edge.origin] = True
            connected[edge.target] = True

        return changes

    def remove_connected_nodes(self, nodes, connected):
        removed = []
        for n in connected.keys():
            if connected[n]:
                nodes.remove(n)
                removed.append(n)

        return removed

    def is_graph_directed(self):
        if len(self.get_edges()) > 0:
            return list(self.get_edges())[0].is_directed

    def find_conture_nodes(self):
        """
        Returns nodes with no incoming edges.
        """
        self._nodes_to_contour = []
        self.visited = []
        for node in self.nodes:
            if node not in self._nodes_to_contour:
                self.path = []
                self.has_cycle_directed(node)

        return self._nodes_to_contour

    def has_cycle_directed(self, node):
        if node in self.path:
            if self.path[0] not in self._nodes_to_contour:
                self._nodes_to_contour.append(self.path[0])
            return
        if node in self.visited_nodes:
            return
        self.path.append(node)
        for edge in node.edges:
            self.has_cycle_directed(edge.target)
        if node not in self._nodes_to_contour:
            self._visited_nodes.append(node)

    def has_cycle_undirected(self):
        """
        Checks for cycles in an undirected graph using DFS.
        """
        self.visited = []
        for node in self.nodes:
            if node in self.visited:
                if node != self.visited[-1]:
                    continue
            if self.depth_first_search(node, None):
                return True
        return False

    def depth_first_search(self, current, parent):
        self._visited_nodes.append(current)
        for node in self.nodes:
            if current.is_related(node):
                if parent and node == parent:
                    continue
                if node in self._visited_nodes:
                    if node != self._visited_nodes[-1]:
                        return True
                elif self.depth_first_search(node, current):
                    return True
        return False

    def find_not_destination_nodes(self):
        """
        Returns nodes with no outgoing edges.
        """
        dict = {}
        for node in self.nodes:
            dict[node] = False

        for edge in self.get_edges():
            dict[edge.target] = True

        roots = []
        for node in dict.keys():
            if dict[node] is False:
                roots.append(node)

        return roots


class NodeIdGenerator:

    def __init__(self):
        self.__current_id = 0

    def next(self):
        self.__current_id += 1
        return self.__current_id - 1

    def reset(self):
        self.__current_id = 0


nodeId = NodeIdGenerator()


class TreeNode(object):
    """
    Represents a node in a tree view (hierarchical structure).

    Attributes:
        object (Node | Edge): Original graph object.
        parent (TreeNode): Parent node in the tree.
        label (str): Relationship label.
        children (List[TreeNode]): Child tree nodes.
        open (bool): Whether the node is expanded.
    """
    def __init__(self, object, parent, type):
        self._opened = False
        self._object = object
        self._object_type = type
        self._id = nodeId.next()
        self._children = []
        self._parent = parent

    @property
    def id(self):
        return self._id

    @property
    def opened(self):
        return self._opened

    @opened.setter
    def opened(self, value):
        self._opened = value

    @property
    def object(self):
        return self._object

    @property
    def object_type(self):
        return self._object_type

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, value):
        self._children = value

    @property
    def parent(self):
        return self._parent

    def open(self):
        self._opened = True
        if len(self._children) <= 0:
            if self._object_type == "node":
                self.add_children(self._object.get_relations())
            else:
                self.add_children(self._parent.object.get_related_nodes(self._object))

    def load_children(self):
        if len(self._children) <= 0:
            if self._object_type == "node":
                self.add_children(self._object.get_relations())
            else:
                self.add_children(self._parent.object.get_related_nodes(self._object))

    def open_parents(self):
        self.open()
        if self._parent:
            self._parent.open_parents()

    def close(self):
        self._opened = False

    def find_node(self, id):
        if id == self._id:
            return self
        else:
            for child in self._children:
                found_node = child.find_node(id)
                if found_node:
                    return found_node
        return None

    def add_children(self, children_objects):
        for child in children_objects:
            if self._object_type == "node":
                child_type = "edge"
            else:
                child_type = "node"
            child_node = TreeNode(child, self, child_type)
            self._children.append(child_node)


class Tree(object):
    """
    Represents the entire tree (hierarchical graph structure).

    Attributes:
        roots (List[TreeNode]): List of root nodes.
    """
    def __init__(self, roots=None):
        nodeId.reset()
        self._roots = roots if roots is not None else []

    def empty(self):
        self._roots = []
        nodeId.reset()

    @property
    def roots(self):
        return self._roots

    @roots.setter
    def roots(self, roots):
        self._roots = roots

    def find_tree_node(self, id):
        for root_node in self._roots:
            found_node = root_node.find_node(id)
            if found_node:
                return found_node
        return None

    def find_node_by_node_id(self, id, nodes=None): # by graph node
        if nodes is None:
            nodes = self._roots
        new_nodes = []
        for node in nodes:
            # if node.object_type != "edge" and node.object.id == id:
            if node.object_type != "edge" and str(node.object.id) == str(id):
                return node
            node.load_children()
            new_nodes += node.children
        if not new_nodes:
            return None
        return self.find_node_by_node_id(id, new_nodes)

    def open_node_by_id(self, id):
        node = self.find_node_by_node_id(id)
        if node:
            node.open_parents()
