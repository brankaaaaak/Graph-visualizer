import json
import os
import time
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from api.models import Edge, Graph, Node
from simple_visualizer.plugin.visualizer.simple_visualizer import SimpleVisualizer
from api.models import Edge, Graph, Node
from django.apps.registry import apps
from simple_visualizer.plugin.visualizer.simple_visualizer import SimpleVisualizer
import xml.etree.ElementTree as ET

def index_view(request):
    api_config = apps.get_app_config('api')
    visualizers = api_config.visualizers
    visualizer_names = [v.name() for v in visualizers]

    return render(request, 'index.html', {
        'visualizers': visualizer_names,
    })
def check_extension(loader_name, file):
    match loader_name:
        case "XmlLoader":
            return file.name.endswith('.xml')
        case "JsonLoader":
            return file.name.endswith('.json')
    return False
def upload_file(request):
    loaders = apps.get_app_config('api').loaders
    chosen_file = request.FILES.get('graph_file')

    for loader in loaders:
        if check_extension(loader.identifier(), chosen_file):
            root_element= loader.load_file(chosen_file, key_field="id")
            graph = loader.make_graph(root_element)
            apps.get_app_config('api').graph = graph
            break
    return render(request, 'index.html')
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

    edge1 = Edge(origin=node1, target=node2, relation="connects", weight=1, directed=False)
    edge2 = Edge(origin=node2, target=node3, relation="connects", weight=1, directed=False)

    node1.add_edge(edge1)
    node2.add_edge(edge1)
    node2.add_edge(edge2)
    node3.add_edge(edge2)

    visualizer = SimpleVisualizer()
    html_snippet = visualizer.visualize(graph, request)

    return render(request, 'index.html', {"view_html": html_snippet})

def choose_visualizer(request):
    choice = request.GET.get('visualizer')

    if choice == 'simple':
        return redirect('simple_visualization')
    elif choice == 'complex':
        return redirect('complex_visualization')
    else:
        return HttpResponse("Invalid choice.")
def simple_visualization(request):
    visualizers = apps.get_app_config('api').visualizers
    graph = apps.get_app_config('api').graph
    
    for v in visualizers:
        if v.identifier() == "simple-visualizer":
            visualizer = SimpleVisualizer()
            html_snippet = visualizer.visualize(graph, request)
    time.sleep(2)

    graph = apps.get_app_config('api').graph
    visualizers = []
    for v in apps.get_app_config('api').visualizers:
        visualizers.append(
            {"name": v.name(), "identifier": v.identifier()})
    loaders = []
    for l in apps.get_app_config('api').loaders:
        loaders.append(
            {"name": l.name(), "identifier": l.identifier()})
    
    return render(request, "index.html", {"view_html":html_snippet})


def complex_visualization(request):
    pass
       
