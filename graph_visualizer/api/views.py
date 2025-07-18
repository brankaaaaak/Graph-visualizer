from django.http import HttpResponse
from django.shortcuts import render

from api.models import Edge, Graph, Node
from block_visualizer.plugin.visualizer.block_visualizer import BlockVisualizer
from simple_visualizer.plugin.visualizer.simple_visualizer import SimpleVisualizer
def index_view(request):
    return render(request, 'index.html')

from django.shortcuts import render
from api.models import Edge, Graph, Node
from simple_visualizer.plugin.visualizer.simple_visualizer import SimpleVisualizer

def test_graph_view(request):
    # Kreiraj graf
    graph = Graph()

    node1 = Node(id=1)
    node2 = Node(id=2)
    node3 = Node(id=3)

    node1.add_attribute("name", "Node 1")
    node2.add_attribute("name", "Node 2")
    node3.add_attribute("name", "Node 3")

    graph.insert_node(node1)
    graph.insert_node(node2)
    graph.insert_node(node3)

    edge1 = Edge(origin=node1, target=node2, relation="connects", weight=1, is_directed=False)
    edge2 = Edge(origin=node2, target=node3, relation="connects", weight=1, is_directed=False)

    node1.add_edge(edge1)
    node2.add_edge(edge1)
    node2.add_edge(edge2)
    node3.add_edge(edge2)

    visualizer = BlockVisualizer()
    #visualizer = SimpleVisualizer()
    html_snippet = visualizer.visualize(graph, request)
    print(html_snippet)

    return render(request, 'index.html', {"view_html": html_snippet})
