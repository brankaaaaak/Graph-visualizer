
from api.services.loader import BaseLoader
import xml.etree.ElementTree as ET
from api.models import Edge, Graph, Node

class XmlLoader(BaseLoader):

    def __init__(self):
        self._id_sequence = 0
        self._key_field = "id"
    
    def identifier(self):
        return "XmlLoader"

    def name(self):
        return "XML Loader"
    
    def load_file(self,xml_file,key_field):
        self._key_field = key_field
        xml_string = xml_file.read()
        xml_root = ET.fromstring(xml_string)
        return xml_root
    
    def make_graph(self, root_element):
        self._id_sequence = 0
        graph = Graph()
        self.create_node(graph, root_element)
        return graph

    def create_node(self, graph, elem):
        self._id_sequence += 1
        node = Node(self._id_sequence)

        for key, value in elem.attrib.items():
            node.add_attribute(key, value)

        for child in elem:
            if not isinstance(child, ET.Element):
                continue

            # Ako dete ima podstablo - napravi novi čvor i poveži ga
            if len(child):  # ima decu, znači pravi čvor
                child_node = self.create_node(graph, child)
                edge = Edge(origin=node, target=child_node, relation=child.tag, weight=0, directed=True)
                node.add_edge(edge)
            else:
                # Nema dece - to je atribut, dodaj ga kao atribut roditeljskom čvoru
                text = child.text.strip() if child.text else ''
                if text:
                    node.add_attribute(child.tag, text)

        if node not in graph.nodes:
            graph.insert_node(node)

        return node
