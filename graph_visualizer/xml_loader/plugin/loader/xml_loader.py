
from api.services.loader import BaseLoader
import xml.etree.ElementTree as ET

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
    

    
    