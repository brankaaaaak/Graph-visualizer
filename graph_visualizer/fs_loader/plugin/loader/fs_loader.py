import os
import datetime
from api.models import Edge, Graph, Node
from api.services.loader import BaseLoader


class FileSystemLoader(BaseLoader):

    def __init__(self):
        self._id_sequence = 0
        self._visited = set()

    def identifier(self):
        return "FileSystemLoader"

    def name(self):
        return "File System Loader"

    def load_file(self, file_object, key_field=None):
        base_path = file_object.read().strip() if hasattr(file_object, "read") else str(file_object)
        return base_path

    def make_graph(self, base_path):
        self._id_sequence = 0
        self._visited = set()
        graph = Graph()
        self._create_node(graph, base_path, None, depth=0)
        return graph

    def _create_node(self, graph, path, parent_node, depth=0):
        abs_path = os.path.abspath(path)
        if abs_path in self._visited:
            return None
        self._visited.add(abs_path)

        self._id_sequence += 1
        node = Node(self._id_sequence)
        node.add_attribute("depth", depth)
        node.add_attribute("name", os.path.basename(abs_path) or abs_path)
        node.add_attribute("path", abs_path)
        node.add_attribute("type", "directory" if os.path.isdir(abs_path) else "file")

        try:
            stat = os.stat(abs_path)
            node.add_attribute("size", stat.st_size)
            node.add_attribute("modified", datetime.datetime.fromtimestamp(stat.st_mtime).date())
        except Exception:
            pass

        graph.insert_node(node)

        if parent_node:
            edge = Edge(origin=parent_node, target=node, relation="contains", weight=0, directed=True)
            parent_node.add_edge(edge)

        '''if os.path.isdir(abs_path):
            try:
                for child in os.listdir(abs_path):
                    child_path = os.path.join(abs_path, child)
                    self._create_node(graph, child_path, node)
            except Exception:
                pass'''

        if os.path.isdir(abs_path):
            try:
                children = os.listdir(abs_path)
                node.add_attribute("num_children", len(children))
                for child in children:
                    child_path = os.path.join(abs_path, child)
                    self._create_node(graph, child_path, node, depth=depth+1)
            except Exception:
                node.add_attribute("num_children", 0)

        return node
