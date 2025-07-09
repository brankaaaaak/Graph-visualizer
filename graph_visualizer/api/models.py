from django.db import models

# Create your models here.
class Node:
    def __init__(self, id):
        self._id = id
        self._edges = []
        self._attributes = {}

    def __hash__(self):
        return hash(self._id)

    def degree(self):
        return len(self._edges)
    
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

class Edge:
    def __init__(self, origin, target, relation, weight, is_directed):
        self._origin = origin
        self._target = target
        self._relation = relation
        self._weight = weight
        self._is_directed = is_directed
    
    @property
    def is_directed(self):
        return self.is_directed

    def __hash__(self):
        return hash((self._origin,self._target))
    
    def __str__(self):
        return f'({self._origin}, {self._target}, {self._relation}, {self._weight}, {self._is_directed})'
    
    def __eq__(self, other) -> bool:
        if self._relation_name != other.relation_name:
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
    
