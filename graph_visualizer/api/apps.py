from django.apps import AppConfig
import pkg_resources

from api.models import Tree, TreeNode


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    loaders = []
    visualizers = []
    tree = None
    base_graph = None
    graph= None
    visualizer=None
    loader=None

    def ready(self):
        self.loaders = load_plugins("loader")
        self.visualizers = load_plugins("visualizer")
        print(len(self.loaders))
        print(len(self.visualizers))

    def get_loader(self, id):
        print(id)
        for loader in self.loaders:
            print(loader.identifier())
            if loader.identifier() == id:
                return loader
        return None

    def get_visualizer(self, id):
        print(id)
        for visualizer in self.visualizers:
            print(visualizer.identifier())
            if visualizer.identifier() == id:
                return visualizer
        return None
    
    def load_tree(self):
        self.tree = Tree()
        for node in find_root_nodes(self.graph.find_subgraphs()):
            print(f"🌳 Root node: {node} ({type(node)})")
            self.tree.roots.append(TreeNode(node, None, "node"))


def load_plugins(entry_point):
    plugins = []
    for ep in pkg_resources.iter_entry_points(group=entry_point):
        print(ep)
        p = ep.load()
        plugin = p()
        plugins.append(plugin)
    return plugins

def find_root_nodes(subgraphs):
    roots = []
    for graph in subgraphs:
        if graph.is_graph_directed():
            contour_nodes = graph.find_conture_nodes()
            hanging_nodes = graph.find_not_destination_nodes()
            roots += merge_lists_distinct(contour_nodes, hanging_nodes)

        else:
            if graph.has_cycle_undirected():
                if len(graph.nodes) > 0:
                    roots.append(graph.nodes[0])
            else:
                for n in graph.nodes:
                    if n.degree() <= 1:
                        roots.append(n)
    return roots

def merge_lists_distinct(first_list, second_list):
    for i in first_list:
        if i not in second_list:
            second_list.append(i)

    return second_list

def print_tree(tree):
    def print_node(node, level=0):
        indent = "  " * level
        print(f"{indent}- Node ID: {node.object.id}, Label: {getattr(node, 'label', 'N/A')}")
        for child in getattr(node, "children", []):
            print_node(child, level + 1)

    for root in tree.roots:
        print_node(root)
