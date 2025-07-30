from api.services.loader import BaseLoader
from api.models import Edge, Graph, Node
import rdflib


class RDFLoader(BaseLoader):

    def __init__(self):
        self._key_field = "id"
        self._node_map = {}  # Map from original RDF URI to Node
        self._id_map = {}  # Map from URI to integer ID
        self._id_sequence = 0  # Internal counter

    def identifier(self):
        return "RDFLoader"

    def name(self):
        return "RDF Loader"

    def load_file(self, rdf_file, key_field):
        self._key_field = key_field
        rdf_data = rdf_file.read()
        self._rdf_graph = rdflib.Graph()
        self._rdf_graph.parse(data=rdf_data)
        return self._rdf_graph

    def make_graph(self, rdf_graph):
        graph = Graph()
        self._node_map.clear()
        self._id_map.clear()
        self._id_sequence = 0

        for subj, pred, obj in rdf_graph:
            subj_id = str(subj)
            obj_id = str(obj)
            pred_label = str(pred)

            subj_node = self._get_or_create_node(subj_id)

            if isinstance(obj, rdflib.Literal):
                subj_node.add_attribute(pred_label, obj.value)
            else:
                obj_node = self._get_or_create_node(obj_id)
                edge = Edge(origin=subj_node, target=obj_node, relation=pred_label, weight=1.0, directed=True)
                subj_node.add_edge(edge)

        # Ubacujemo sve cvorove u graf
        for node in self._node_map.values():
            graph.insert_node(node)

        return graph

    def _get_or_create_node(self, original_id):
        if original_id not in self._node_map:
            self._id_sequence += 1
            numeric_id = self._id_sequence
            node = Node(numeric_id)
            node.add_attribute(self._key_field, original_id)  # cuvamo originalni RDF URI kao atribut
            self._node_map[original_id] = node
            self._id_map[original_id] = numeric_id
        return self._node_map[original_id]
