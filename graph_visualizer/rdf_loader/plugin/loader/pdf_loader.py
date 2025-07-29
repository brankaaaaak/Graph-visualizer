from rdflib import Graph as RDFGraph
from api.models import Graph, Node, Edge
from api.services.loader import BaseLoader


class RDFLoader(BaseLoader):

    def __init__(self):
        self._graph = None

    def identifier(self):
        return "RDFLoader"

    def name(self):
        return "RDF Turtle Loader"

    def load_file(self, rdf_file, key_field=None):
        rdf_data = rdf_file.read()
        rdf_graph = RDFGraph()
        rdf_graph.parse(data=rdf_data, format="turtle")
        return rdf_graph

    def make_graph(self, rdf_graph):
        self._graph = Graph()
        node_map = {}

        for subj, pred, obj in rdf_graph:
            subj_str = str(subj)
            obj_str = str(obj)
            pred_str = str(pred)

            # Dodaj subjekat ako ne postoji
            if subj_str not in node_map:
                subj_node = Node(subj_str)
                subj_node.add_attribute("uri", subj_str)
                self._graph.insert_node(subj_node)
                node_map[subj_str] = subj_node

            # Dodaj objekat ako ne postoji
            if obj_str not in node_map:
                obj_node = Node(obj_str)
                obj_node.add_attribute("uri", obj_str)
                self._graph.insert_node(obj_node)
                node_map[obj_str] = obj_node

            # Dodaj ivicu
            edge = Edge(
                origin=node_map[subj_str],
                target=node_map[obj_str],
                label=pred_str,
                weight=1,
                directed=True
            )
            node_map[subj_str].add_edge(edge)

        return self._graph
