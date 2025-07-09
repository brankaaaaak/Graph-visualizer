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
