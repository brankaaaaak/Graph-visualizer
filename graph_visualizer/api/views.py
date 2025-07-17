import json
import os
import pprint
from django.http import HttpResponse, JsonResponse
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
"""
def upload_file(request):
    loaders = apps.get_app_config('api').loaders

    chosen_file = request.FILES.get('graph_file')
    file_missing = False
    extension_missmatch = False

    ext = os.path.splitext(chosen_file.name)[1].lower()

    graph = None
    for loader in loaders:
        if check_extension(loader.identifier(), chosen_file):
                raw_graph = loader.load_file(chosen_file, key_field="id")
                graph = dict_to_graph(raw_graph)
                print("Loaded graph:")
                print(graph)
                break
    if not graph:
        return render(request, 'index.html', {"error": "Unsupported file type or loading failed."})
    
    api_config = apps.get_app_config('api')
    api_config.current_graph = graph
    api_config.current_graph = graph

    api_config.load_tree()

    tree = api_config.tree
    tree_html = render_tree_html(tree)


    return render(request, 'index.html', {
        "tree_html": tree_html,
        "visualizers": [v.name() for v in api_config.visualizers]
    })
"""
def upload_file(request):
    api_config = apps.get_app_config('api')
    loaders = api_config.loaders
    chosen_file = request.FILES.get('graph_file')

    raw_graph = None
    for loader in loaders:
        if check_extension(loader.identifier(), chosen_file):
                raw_graph = loader.load_file(chosen_file, key_field="id")
                api_config.base_graph = loader.make_graph(raw_graph)                 
                api_config.current_graph = api_config.base_graph
                break
    if not raw_graph:
        return render(request, 'index.html', {"error": "Unsupported file type or loading failed."})

    """for node in api_config.current_graph.nodes:
        print(f"ID: {node.id}")
        print(f"Atributi: {node.attributes}")
        print(f"Broj veza (edges): {len(node.edges)}")
        print("====")"""
    # Inicijalizuj strukturu stabla
    api_config.load_tree()
    tree_html = generate_tree_html(api_config.tree.roots)


    # Prikaži stranicu sa grafom i listom vizualizera
    return render(request, 'index.html', {
        "tree_html": tree_html,
        "visualizers": [v.name() for v in api_config.visualizers]
    })


def check_extension(loader_name, file):
    match loader_name:
        case "XmlLoader":
            return file.name.endswith('.xml')
        case "JsonLoader":
            return file.name.endswith('.json')
    return False


def render_tree_html(forest):
    def render_node(node):
        arrow = "➖" if getattr(node, 'opened', False) else "➕"
        html = f'<li>'
        html += f'<a href="#" class="node-toggle" data-node-id="{node.id}">{arrow} Node {node.object.id}</a>'

        children = getattr(node, 'children', [])
        if children and getattr(node, 'opened', False):
            html += '<ul>'
            for child in children:
                label = "Edge" if getattr(child, 'is_edge', False) else "Node"
                arrow_child = "➖" if getattr(child, 'opened', False) else "➕"
                html += '<li>'
                html += f'<a href="#" class="node-toggle" data-node-id="{child.id}">{arrow_child} {label} {getattr(child.object, "id", "")}</a>'

                grandchildren = getattr(child, 'children', [])
                if grandchildren and getattr(child, 'opened', False):
                    html += '<ul>'
                    for grandchild in grandchildren:
                        html += render_node(grandchild)
                    html += '</ul>'
                html += '</li>'
            html += '</ul>'
        html += '</li>'
        return html

    html = '<ul class="tree-list">'
    for root in forest.roots:
        html += render_node(root)
    html += '</ul>'
    return html

def generate_tree_html(nodes):
    html = '<ul class="tree-list">'
    for node in nodes:
        if not hasattr(node, 'id') or not hasattr(node, 'object'):
            print("⚠️ Upozorenje: Čvor nije validan TreeNode →", node)
            continue

        arrow = "➖" if node.opened else "➕"

        # Priprema teksta za prikaz
        
        if isinstance(node.object, Node):
            label = "Node"
            text = f"<strong>{node.object.id}</strong> - {node.object.attributes}"
        elif isinstance(node.object, str):  # relacija kao "hobbies"
            label = "Edge"
            text = f"<em>{node.object}</em>"
        else:
            label = "Unknown"
            text = str(node.object)

        # Renderuj ovaj čvor
        html += f'''
        <li>
            <a href="#" class="node-toggle" data-node-id="{node.id}">{arrow} {label}: {text}</a>
        '''

        # Ako je čvor otvoren i ima djecu, rekurzivno prikaži
        if node.opened and node.children:
            html += generate_tree_html(node.children)

        html += '</li>'
    html += '</ul>'
    return html




def dict_to_graph(graph_dict):
    graph = Graph()
    nodes_map = {}

    def add_node_recursive(node_dict):
        node = Node(node_dict['id'])
        for k, v in node_dict.items():
            if k != 'children':
                node.add_attribute(k, v)
        graph.insert_node(node)
        nodes_map[node.id] = node

        for child_dict in node_dict.get('children', []):
            child_node = add_node_recursive(child_dict)
            edge = Edge(origin=node, target=child_node, relation="parent-child", weight=1, is_directed=True)
            node.add_edge(edge)
            child_node.add_edge(edge)
        return node

    add_node_recursive(graph_dict)
    return graph

def expand_node_view(request):
    try:
        node_id = int(request.GET.get('node_id'))
        api_config = apps.get_app_config('api')
        tree_node = api_config.tree.find_tree_node(node_id)

        if tree_node is None:
            return JsonResponse({"error": "Node not found"}, status=404)

        tree_node.open()
        children_html = generate_tree_html(tree_node.children)
        return JsonResponse({"html": children_html})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)



