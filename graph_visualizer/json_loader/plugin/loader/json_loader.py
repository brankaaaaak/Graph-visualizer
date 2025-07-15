import numbers
from api.models import Edge, Graph, Node
from api.services.loader import BaseLoader
import json

class JsonLoader(BaseLoader):
    
    def __init__(self):
        self._id_sequence = 0
        self._key_field = "id"
        self._graph = None
    
    def identifier(self):
        return "JsonLoader"

    def name(self):
        return "JSON Loader"
    
    def load_json(self, json_file, key_field):
        if key_field:
            self._key_field = key_field
        json_object = json.load(json_file)
        return json_object
    
    def make_graph(self, tree):
        self._graph = Graph()
        return self._graph

    def create_node(self, data, parent=None, relation=None):
        current_node = Node(None)

        if isinstance(data, dict):
            for key, value in data.items():
                if is_primitive(value):
                    if key == self._key_field:
                        current_node.id = value
                        current_node.add_attribute("id", value)
                        self.next_id()
                    else:
                        if current_node.id is None:
                            current_node.id = self.next_id()
                        current_node.add_attribute(key, value)
                elif isinstance(value, dict) or isinstance(value, list):
                    self.create_node(value, current_node, key)
        elif isinstance(data, list):
            for element in data:
                if isinstance(element, dict):
                    node = self.create_node(element, parent, relation)
                    node.id = self.set_node_id(element)
                    self.update_graph(node, parent, relation)
                elif is_primitive(element):
                    node = Node(element)
                    node.add_attribute("id", element)
                    node.add_attribute("value", element)
                    self.update_graph(node, parent, relation)

        if current_node.id is None:
            return parent

        self.alter_existing_node(current_node)
        if parent:
            self.add_new_edge(current_node, parent, relation)

        return current_node


    def set_node_id(self, data):
        if isinstance(data, dict) and self._key_field in data:
            return data[self._key_field]
        return self.next_id()
    
    def next_id(self):
        current_id = self._id_sequence
        self._id_sequence += 1
        return current_id
    
    def update_graph(self, node, parent, relation):
        self.alter_existing_node(node)
        self.add_new_edge(node, parent, relation)

    def add_new_edge(self, child_node, parent_node, relation):
        edge = Edge(parent_node, child_node, relation, 0, True)
        parent_node.add_edge(edge)

    def alter_existing_node(self, node):
        is_present = self._graph.has_node(node)
        if is_present:
            node.attributes.update(is_present.attributes)
            self.alter_existing_edges(self._graph.edges(), node)
        self._graph.insert_node(node)

    def alter_existing_edges(self, edges, node):
        for edge in edges:
            if edge.origin == node:
                edge.origin = node
                node.add_edge(edge)
            elif edge.target == node:
                edge.target = node
                edge.origin.add_edge(edge)

def is_primitive(value):
    return isinstance(value, (str, numbers.Number))
