import json
import re
from django.http import HttpResponse, JsonResponse
import time
from django.http import HttpResponse
from django.shortcuts import  render
from django.shortcuts import render
from api.models import Edge, Graph, Node, TreeNode
from block_visualizer.plugin.visualizer.block_visualizer import BlockVisualizer
from simple_visualizer.plugin.visualizer.simple_visualizer import SimpleVisualizer
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

    api_config.base_graph=None
    api_config.graph =None
    api_config.tree=None
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

        if isinstance(node.object, Node):
            label = "Node"
            text = f"<strong>{node.object.id}</strong> - {node.object.attributes}"
            data_attr = f'data-node-id="{node.id}" data-graph-node-id="{node.object.id}"'
        elif isinstance(node.object, str):  
            label = "Edge"
            text = f"<em>{node.object}</em>"
            data_attr = f'data-edge-id="{node.id}"'
        else:
            label = "Unknown"
            text = str(node.object)
            data_attr = ''

        # Renderuj ovaj čvor
        html += f'''
        <li>
            <a href="#" class="node-toggle" {data_attr}>{arrow} {label}: {text}</a>
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
            return render(request, "index.html", {"view_html": html_snippet, "tree_html": tree_html,"graph_loaded":graph,"current_visualizer":v.identifier()})
    
    return HttpResponse("Invalid visualizer identifier.", status=404)

def check_extension(loader_name, file):
    match loader_name:
        case "XmlLoader":
            return file.name.endswith('.xml')
        case "JsonLoader":
            return file.name.endswith('.json')
    return False  

def create_node(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        node_id = data.get("id")
        props = data.get("properties", {})

        if not node_id:
            return JsonResponse({"error": "Missing node ID."}, status=400)

        api_config = apps.get_app_config("api")

        if api_config.graph.get_node(node_id):
            return JsonResponse({"error": f"Node '{node_id}' already exists."}, status=400)

        new_node = Node(node_id)
        for key, value in props.items():
            new_node.add_attribute(key, value)

        api_config.graph.insert_node(new_node)

        api_config.tree.roots.append(TreeNode(new_node, None, "node"))

        api_config.load_tree()

        return JsonResponse({
            "success": True
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
def create_edge(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)

        edge_id = data.get("id")
        source_id = data.get("source")
        target_id = data.get("target")
        relation = data.get("relation")
        weight = data.get("weight", 1)  
        directed = data.get("directed", False)  

        if not edge_id or not source_id or not target_id or not relation:
            return JsonResponse({"error": "Missing edge id, source, target or relation."}, status=400)

        api_config = apps.get_app_config("api")
        graph = api_config.graph

        source_node = graph.get_node(source_id)
        target_node = graph.get_node(target_id)

        if not source_node or not target_node:
            return JsonResponse({"error": "Source or target node not found."}, status=404)

        new_edge = Edge(
            origin=source_node,
            target=target_node,
            relation=relation,
            weight=weight,
            directed=directed
        )

        graph.insert_edge(new_edge)

        api_config.load_tree()  # ako treba reload

        return JsonResponse({"success": True})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
def delete_node(request):
    api_config = apps.get_app_config("api")
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        node_id = data.get("id")

        node = api_config.graph.get_node(node_id)
        if not node:
            return JsonResponse({"error": f"Node '{node_id}' not found."}, status=404)
        if node.edges:
            return JsonResponse({"error": "Node has edges."}, status=400)
        
        success = api_config.graph.remove_node(node)
        if not success:
            return JsonResponse({"success": False, "error": "Veza nije pronađena."})

        visualizer = api_config.visualizers[0]
        html_snippet = visualizer.visualize(api_config.graph, request)
        api_config.load_tree()
        tree_html = generate_tree_html(api_config.tree.roots)

        return JsonResponse({
            "success": True,
            "view_html": html_snippet,
            "tree_html": tree_html
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
    
def delete_edge(request):

    api_config = apps.get_app_config('api')
    graph = apps.get_app_config('api').graph
    if request.method == "POST":
        data = json.loads(request.body)
        origin = data.get("origin")
        target = data.get("target")
        relation = data.get("relation")
        

        try:
            
            success = graph.remove_edge(origin, target, relation)
            if not success:
                return JsonResponse({"success": False, "error": "Veza nije pronađena."})

            visualizer = api_config.visualizers[0]
            html_snippet = visualizer.visualize(graph, request)
            api_config.load_tree()
            tree_html = generate_tree_html(api_config.tree.roots)

            return JsonResponse({
                "success": True,
                "view_html": html_snippet,
                "tree_html": tree_html
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"success": False, "error": str(e)})
        
def edit_node(request):
    api_config = apps.get_app_config('api')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            node_id = data.get('id')
            properties = data.get('properties', {})

            if not node_id:
                return JsonResponse({'success': False, 'error': 'Node ID is required'})
            
            if not isinstance(properties, dict) or len(properties) != 1:
                return JsonResponse({'success': False, 'error': 'Exactly one property must be provided'})
            node = api_config.graph.get_node(node_id)
            if not node:
                return JsonResponse({'success': False, 'error': 'Node not found'})
            key, value = next(iter(properties.items()))
            success = api_config.graph.update_node(node, key, value)
            if not success:
                return JsonResponse({"success": False, "error": "Veza nije pronađena."})

            visualizer = api_config.visualizers[0]
            html_snippet = visualizer.visualize(api_config.graph, request)
            api_config.load_tree()
            tree_html = generate_tree_html(api_config.tree.roots)

            return JsonResponse({
                "success": True,
                "view_html": html_snippet,
                "tree_html": tree_html
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Only POST allowed'})

def search(request):
        query = request.GET.get("query", "")
        if not query:
            return JsonResponse({"success": False, "error": "Query is required"}, status=400)

        old_graph = apps.get_app_config('api').graph
        if old_graph is None:
            return JsonResponse({"success": False, "error": "No graph loaded"}, status=400)

        new_graph = Graph()

        for node in old_graph.get_nodes():
            search_node(new_graph, node, query)

        # napravi novi graf samo sa pronađenim čvorovima i granama
        apps.get_app_config('api').graph = create_graph(old_graph, new_graph)
        apps.get_app_config('api').load_tree()

        return JsonResponse({
            "success": True
        })

def search_node(new_graph, node, query):
    found = False
    query = query.strip().lower()

    for key, value in node.attributes.items():
        if query in str(key).lower() or query in str(value).lower():
            found = True
            break

    if query in str(node.id).lower():
        found = True

    if found:
        new_node = Node(node.id)
        for key, value in node.attributes.items():
            new_node.add_attribute(key, value)
        new_graph.insert_node(new_node)
        
def create_graph(original_graph, filtered_graph):
    new_graph = Graph()

    for node in filtered_graph.nodes:
        new_graph.insert_node(node)

    for node in filtered_graph.nodes:
        original_node = original_graph.get_node(node.id)
        if original_node:
            for edge in original_node.edges:
                origin_id = edge.origin.id
                target_id = edge.target.id

                if new_graph.get_node(origin_id) and new_graph.get_node(target_id):
                    new_edge = Edge(
                        origin=new_graph.get_node(origin_id),
                        target=new_graph.get_node(target_id),
                        relation=edge.relation,
                        weight=edge.weight,
                        directed=edge.directed
                    )
                    new_graph.insert_edge(new_edge)

    return new_graph
def clear_graph(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    
    try:
        api_config = apps.get_app_config('api')
        api_config.graph = None
        api_config.base_graph = None
        api_config.tree = None
        api_config.current_visualizer = None
        
        return JsonResponse({"success": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
def filter_view(request):
    import re
    condition = request.GET.get("condition", "")
    if not condition:
        return JsonResponse({"success": False, "error": "Condition is required"}, status=400)

    old_graph = apps.get_app_config('api').graph
    if old_graph is None:
        return JsonResponse({"success": False, "error": "No graph loaded"}, status=400)

    # Format: key operator value (e.g., Age > 20)
    match = re.match(r"(\w+)\s*(==|=|!=|<=|>=|<|>)\s*['\"]?([\w\s]+)['\"]?", condition)
    if not match:
        return JsonResponse({"success": False, "error": "Invalid filter format"}, status=400)

    key, operator, value = match.groups()
    try:
        value = int(value)
    except ValueError:
        pass  # ostaje string

    def match_condition(props):
        if not props:
            return False
        node_val = props.get(key)
        if node_val is None:
            return False
        if isinstance(value, int) and isinstance(node_val, str) and node_val.isdigit():
            node_val = int(node_val)
        try:
            if operator in ("=", "=="):
                return node_val == value
            elif operator == "!=":
                return node_val != value
            elif operator == "<":
                return node_val < value
            elif operator == ">":
                return node_val > value
            elif operator == "<=":
                return node_val <= value
            elif operator == ">=":
                return node_val >= value
        except:
            return False
        return False

    new_graph = Graph()
    for node in old_graph.get_nodes():
        if match_condition(node.get_attributes()):
            new_graph.insert_node(node)

    for edge in old_graph.get_edges():
        if new_graph.get_node(edge.origin) and new_graph.get_node(edge.target):
            new_graph.insert_edge(edge)

    apps.get_app_config('api').graph = new_graph
    apps.get_app_config('api').load_tree()

    return JsonResponse({"success": True})


    