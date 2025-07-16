import json
import os
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from api.models import Edge, Graph, Node
from simple_visualizer.plugin.visualizer.simple_visualizer import SimpleVisualizer
from api.models import Edge, Graph, Node
from django.apps.registry import apps
from simple_visualizer.plugin.visualizer.simple_visualizer import SimpleVisualizer

def index_view(request):
    api_config = apps.get_app_config('api')
    visualizers = api_config.visualizers
    visualizer_names = [v.name() for v in visualizers]

    return render(request, 'index.html', {
        'visualizers': visualizer_names,
    })

def upload_file(request):
    loaders = apps.get_app_config('api').loaders

    chosen_file = request.FILES.get('graph_file')
    file_missing = False
    extension_missmatch = False

    ext = os.path.splitext(chosen_file.name)[1].lower()

    for loader in loaders:
        if check_extension(loader.identifier(), chosen_file):
                graph = loader.load_file(chosen_file, key_field="id")   
                print("Loaded graph:")
                print(graph)
                break
    return render(request, 'index.html')

def check_extension(loader_name, file):
    match loader_name:
        case "XmlLoader":
            return file.name.endswith('.xml')
        case "JsonLoader":
            return file.name.endswith('.json')
    return False

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

    visualizer = SimpleVisualizer()
    html_snippet = visualizer.visualize(graph, request)

    return render(request, 'index.html', {"view_html": html_snippet})
