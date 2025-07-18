from django.http import HttpResponse, JsonResponse
import time
from django.http import HttpResponse
from django.shortcuts import  render
from django.shortcuts import render
from api.models import Edge, Graph, Node
from api.models import Edge, Graph, Node
from django.apps.registry import apps
from django.template.loader import render_to_string


def index_view(request):
    api_config = apps.get_app_config('api')
    visualizers = api_config.visualizers
    visualizers_data = [(v.identifier(), v.name()) for v in visualizers]

    return render(request, 'index.html', {
        'visualizers': visualizers_data,
    })

def upload_file(request):
    api_config = apps.get_app_config('api')
    loaders = apps.get_app_config('api').loaders
    chosen_file = request.FILES.get('graph_file')

    raw_graph = None
    for loader in loaders:
        if check_extension(loader.identifier(), chosen_file):
            raw_graph= loader.load_file(chosen_file, key_field="id")
            api_config.base_graph = loader.make_graph(raw_graph)                 
            api_config.graph = api_config.base_graph
            break
    if not raw_graph:
        return render(request, 'index.html', {"error": "Unsupported file type or loading failed."})
    graph = apps.get_app_config('api').graph
    graph_loaded = graph is not None and graph.nodes
   
    visualizers_data = [(v.identifier(), v.name()) for v in api_config.visualizers]

    return render(request, 'index.html', {
        "visualizers": visualizers_data,
        "graph_loaded": graph_loaded
    })

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
        elif isinstance(node.object, str):  
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
    #print(html)
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
        print(request)
        node_id = int(request.GET.get('node_id'))
        print(node_id)
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

def expand_node_from_view(request, node_id):
    try:
        api_config = apps.get_app_config('api')
        tree = api_config.tree
        tree_node = api_config.tree.find_node_by_node_id(node_id)
        if tree_node is None:
            for node in tree.roots:
                node.close()
            tree_html = generate_tree_html(tree.roots)
            return HttpResponse(tree_html)

        for node in tree.roots:
            node.close()

        tree_node.open_parents()
        tree_html = generate_tree_html(tree.roots)

        return HttpResponse(tree_html)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

        
    
def visualize(request):
    api_config = apps.get_app_config('api')
    visualizer_id = request.GET.get('visualizer')
    if not visualizer_id:
        return HttpResponse("No visualizer specified.", status=400)

    graph = apps.get_app_config('api').graph
    visualizers = apps.get_app_config('api').visualizers

    api_config.load_tree()
    tree_html = generate_tree_html(api_config.tree.roots)

    for v in visualizers:
        if v.identifier() == visualizer_id:
            html_snippet = v.visualize(graph, request)
            time.sleep(2)
            return render(request, "index.html", {"view_html": html_snippet, "tree_html": tree_html,"graph_loaded":graph})
    
    return HttpResponse("Invalid visualizer identifier.", status=404)

def check_extension(loader_name, file):
    match loader_name:
        case "XmlLoader":
            return file.name.endswith('.xml')
        case "JsonLoader":
            return file.name.endswith('.json')
    return False      
