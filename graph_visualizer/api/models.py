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
    
    @property
    def attributes(self):
        return self._attributes

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
    def relation(self):
        return self._relation

    @property
    def target(self):
        return self._target

    @property
    def origin(self):
        return self._origin
    
    @property
    def is_directed(self):
        return self.is_directed

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
    def _dfs_cycle_check(self, current_node, parent_node):
            self._visited_nodes.add(current_node)
            for node in self._nodes:
                if current_node.is_related(node):
                    if node == parent_node:
                        continue
                    if node in self._visited_nodes:
                        return True
                    if self._dfs_cycle_check(node, current_node):
                        return True
            return False
    def cycle_check(self):
            self._visited_nodes = set()
            for node in self._nodes:
                if node not in self._visited_nodes:
                    if self._dfs_cycle_check(node, None):
                        return True
            return False
        
