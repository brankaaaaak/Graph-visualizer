
from api.services.loader import BaseLoader
import xml.etree.ElementTree as ET
from api.models import Edge, Graph, Node

class XmlLoader(BaseLoader):
    def __init__(self):
        self._id_sequence = 0
        self._key_field = "id"
        self._graph = None

    def identifier(self):
        return "XmlLoader"

    def name(self):
        return "XML Loader"

    def load_file(self, xml_file, key_field=None):
        if key_field:
            self._key_field = key_field
        tree = ET.parse(xml_file)
        return tree.getroot()

    def make_graph(self, root_element):
        self._graph = Graph()
        self.create_node(root_element)
        return self._graph

    def create_node(self, element, parent_node=None, relation=None):
        node = Node(None)

        if self._key_field in element.attrib:
            node.id = element.attrib[self._key_field]
            node.add_attribute("id", node.id)
        else:
            node.id = self.next_id()

        for key, value in element.attrib.items():
            node.add_attribute(key, value)

        if element.text and element.text.strip():
            node.add_attribute("value", element.text.strip())

        self.alter_existing_node(node)

        if parent_node:
            self.add_new_edge(node, parent_node, relation)

        for child in element:
            self.create_node(child, node, child.tag)

        return node

    def next_id(self):
        current_id = self._id_sequence
        self._id_sequence += 1
        return current_id

    def alter_existing_node(self, node):
        if self._graph.has_node(node):
            node.attributes.update(self._graph.get_node(node.id).attributes)
        self._graph.insert_node(node)

    def add_new_edge(self, child_node, parent_node, relation):
        edge = Edge(parent_node, child_node, relation, 0, True)
        parent_node.add_edge(edge)