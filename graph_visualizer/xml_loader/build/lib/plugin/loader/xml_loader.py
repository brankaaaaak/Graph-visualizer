
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
        graph = Graph()
        self.create_node(graph, root_element)
        return graph
    
    def create_node(self,graph,root_element):
        self._id_sequence+=1
        node=Node(self._id_sequence)
        for key in root_element.attrib:
            node.add_attribute(key,root_element.attrib.get(key))

        root_element = root_element.text.strip()
        if root_element.text:
            root_element.text = " ".join(root_element.text.split())
            node.add_attribute(node.tag, node.text)

        for child in root_element:
            child_node= self.create_node(graph, child)
            edge = Edge(node, child_node, relation=child.tag, weight=0, is_directed=True)
            node.add_edge(edge)

        for n in graph.nodes:
            if node == n:
                return node
        graph.insert_node(node)
        return node




        



    
    