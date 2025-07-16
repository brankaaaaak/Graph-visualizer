
from api.services.loader import BaseLoader
import xml.etree.ElementTree as ET
from api.models import Graph

class XmlLoader(BaseLoader):

    def __init__(self):
        self._id_sequence = 0
        self._key_field = "id"
    
    def identifier(self):
        return "XmlLoader"

    def name(self):
        return "XML Loader"
    
    def load_xml(self,xml_file,key_field):
        self._key_field = key_field
        xml_string = xml_file.read()
        xml_root = ET.fromstring(xml_string)
        return xml_root
    
    def make_graph(self, tree):
        graph = Graph()
        self.create_node(graph, tree)
        return graph
    
    def create_node(graph,tree):
        pass

    
    