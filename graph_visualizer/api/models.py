from django.db import models

# Create your models here.
class Node:
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
        if self.id == value.id:
            return True
        if len(self.edges) != len(value.edges):
            return False
        if self.attributes != value.attributes:
            return False
        return True        
    
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
    def __init__(self, origin, target, relation, weight, is_directed):
        self._origin = origin
        self._target = target
        self._relation = relation
        self._weight = weight
        self._is_directed = is_directed

    @property
    def weight(self):
        return self._weight

    @property
    def relation(self):
        return self._relation

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
        return self._is_directed

    def __hash__(self):
        return hash((self._origin,self._target))
    
    def __str__(self):
        return f'({self._origin}, {self._target}, {self._relation}, {self._weight}, {self._is_directed})'
    
    def __eq__(self, other) -> bool:
        if self._relation != other.relation:
            return False
        elif self._weight != other.weight:
            return False
        elif self._is_directed != other.is_directed:
            return False
        elif self._target != other.target:
            return False
        return True
    
    def get_nodes(self):
        return self._origin, self._target

class Graph:
    def __init__(self):
        self._nodes = []
        self._visited_nodes = []
        self._path = []

    @property
    def nodes(self):
        return self._nodes

    def node_degree(self, node):
        return node.degree()

    def get_edges(self):
        edges = set()
        for node in self._nodes:
            edges.update(node.edges)  
        return edges
    
    def get_number_of_nodes(self):
        return len(self._nodes)
    
    def get_number_of_edges(self):
        directed = sum(1 for edge in self.get_edges() if edge.is_directed())
        undirected = len(self.get_edges()) - directed
        return directed + undirected // 2
    
    def is_directed(self):
        edges = self.get_edges()
        if edges:
            first_edge = list(edges)[0]
            return first_edge.is_directed
        return False
    
    def has_node(self, n):
        for node in self.nodes:
            if n == node:
                return node
        return None
    
    def get_node(self, id):
        return next((node for node in self.nodes if str(node.id) == str(id)), None)

    
    def insert_node(self, node):
        existing_node = self.has_node(node)
        if existing_node:
            self._nodes[self._nodes.index(existing_node)] = node
        else:
            self._nodes.append(node)

    def insert_edge(self, origin, target, relation, weight, is_directed):
        edge = Edge(origin = origin, target= target, relation= relation, weight= weight, is_directed= is_directed)
        origin.add_edge(target)
        if not is_directed:
            target.add_node(origin)


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
    
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def opened(self):
        return self._opened

    @opened.setter
    def opened(self, value):
        self._opened=value
    
    @property
    def object(self):
        return self._object

    @property
    def object_type(self):
        return self._object_type

    @property
    def children(self):
        return self._children

    @property
    def parent(self):
        return self._parent
    
    def find_node(self, id):
        if id == self._id:
            return self
        else:
            for child in self._children:
                found_node = child.find_node(id)
                if found_node:
                    return found_node

    def add_children(self, children_objects):
        for child in children_objects:
            if self._object_type == "vertex":
                child_type = "edge"
                child_node = TreeNode(child, self, child_type)
                self._children.append(child_node)
            else:
                child_type = "vertex"
                child_node = TreeNode(child, self, child_type)
                self._children.append(child_node)
    
    def open(self):
        self._opened = True
        if len(self._children) <= 0:
            if self._object_type == "vertex":
                self.add_children(self._object.relations())
            else:
                self.add_children(self._parent.object.related_vertices(self._object))
    
    def close(self):
        self._opened = False

    def open_parents(self):
        self.open()
        if self._parent:
            self._parent.open_parents()

    def load_children(self):
        if len(self._children) <= 0:
            if self._object_type == "vertex":
                self.add_children(self._object.relations())
            else:
                self.add_children(self._parent.object.related_vertices(self._object))
    

class Tree(object):
    def __init__(self, roots=None):
        nodeId.reset()
        self._roots = roots
        if self._roots is None:
            self._roots = []
        self._last_opened = 0

    @property
    def roots(self):
        return self._roots

    @roots.setter
    def roots(self, roots):
        self._roots = roots

    @property
    def last_opened(self):
        return self._last_opened

    @last_opened.setter
    def last_opened(self, last_opened):
        self._last_opened = last_opened
    
    def find_tree_node(self, id):
        for root_node in self._roots:
            found_node = root_node.find_node(id)
            if found_node:
                return found_node
            
    def iter_nodes(self, nodes=None):
        if nodes is None:
            nodes = self._roots
        for node in nodes:
            yield node
            node.load_children()
            yield from self.iter_nodes(node.children)

    def find_node_by_graph_node_id(self, id):
        for node in self.iter_nodes():
            if node.object_type != "edge" and node.object.id == id:
                return node
        return None

