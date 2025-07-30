import json
import uuid
# import graphviz
from django.http import HttpResponse, JsonResponse
import time
from django.http import HttpResponse
from django.shortcuts import  redirect, render
from django.shortcuts import render
from api.models import Edge, Graph, Node, TreeNode
from django.apps.registry import apps
from graph_platform.core import state


def index_view(request):
    visualizers = state.visualizers
    visualizers_data = [(v.identifier(), v.name()) for v in visualizers]

    return render(request, 'index.html', {
        'visualizers': visualizers_data,
        'current_workspace': state.current_workspace,
        'workspaces': list(state.workspaces.keys()),
    })


def upload_file(request):
    loaders = state.loaders
    chosen_file = request.FILES.get('graph_file')
    raw_graph = None
    state.base_graph=None
    state.graph =None
    state.tree=None
    for loader in state.loaders:
        if check_extension(loader.identifier(), chosen_file):
            raw_graph = loader.load_file(chosen_file, key_field="id")
            state.base_graph = loader.make_graph(raw_graph)
            state.graph = state.base_graph
            state.loader = loader
            break
    
    if not raw_graph:
        return render(request, 'index.html', {"error": "Unsupported file type or loading failed."})
    graph = state.graph
    graph_loaded = graph is not None and graph.nodes
   
    visualizers_data = [(v.identifier(), v.name()) for v in state.visualizers]

    return render(request, 'index.html', {
        "visualizers": visualizers_data,
        "graph_loaded": graph_loaded,
        "current_workspace": state.current_workspace,
        "workspaces": list(state.workspaces.keys()),
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
        tree_node = state.tree.find_tree_node(node_id)
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
        tree = state.tree
        tree_node = state.tree.find_node_by_node_id(node_id)
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
    visualizer_id = request.GET.get('visualizer')
    if not visualizer_id:
        return HttpResponse("No visualizer specified.", status=400)

    graph = state.graph
    visualizers = state.visualizers

    state.load_tree()
    tree_html = generate_tree_html(state.tree.roots)
    # bird_svg = generate_bird_view_svg(graph)

    for v in visualizers:
        if v.identifier() == visualizer_id:
            state.visualizer = v
            html_snippet = v.visualize(graph, request)
            return render(request, "index.html", {
                "view_html": html_snippet,
                "tree_html": tree_html,
                # "bird_svg": bird_svg,
                "graph_visualized": graph,
                "current_visualizer": v.identifier(),
                "current_workspace": state.current_workspace,
                "workspaces": list(state.workspaces.keys())
            })

    return HttpResponse("Invalid visualizer identifier.", status=404)


def check_extension(loader_name, file):
    match loader_name:
        case "XmlLoader":
            return file.name.endswith('.xml')
        case "JsonLoader":
            return file.name.endswith('.json')
        case "RDFLoader":
            return file.name.endswith(".ttl")
        case "FileSystemLoader":
            return file.name.endswith('.fstxt') or file.name.endswith('.folder')
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


        if state.graph.get_node(node_id):
            return JsonResponse({"error": f"Node '{node_id}' already exists."}, status=400)

        new_node = Node(node_id)
        
        if "id" not in props and str(node_id).isdigit():
            props["id"] = int(node_id)
        else:
            props["id"] = node_id

        for key, value in props.items():
            new_node.add_attribute(key, value)

        state.graph.insert_node(new_node)

        state.tree.roots.append(TreeNode(new_node, None, "node"))

        state.load_tree()

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

        source_id = data.get("source")
        target_id = data.get("target")
        relation = data.get("relation")
        weight = data.get("weight", 1)  
        directed = data.get("directed", False)  

        if not source_id or not target_id or not relation:
            return JsonResponse({"error": "Missing edge id, source, target or relation."}, status=400)

        graph = state.graph

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

        state.load_tree() 

        return JsonResponse({"success": True})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


def delete_node(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        node_id = data.get("id")

        node = state.graph.get_node(node_id)
        if not node:
            return JsonResponse({"error": f"Node '{node_id}' not found."}, status=404)
        if node.edges:
            return JsonResponse({"error": "Node has edges."}, status=400)
        
        has_any_edge = False
        for other in state.graph.nodes:
            for edge in other.edges:
                if edge.target == node or edge.origin == node:
                    has_any_edge = True
                    break
            if has_any_edge:
                break

        if has_any_edge:
            return JsonResponse({"error": "Node has incoming or outgoing edges."}, status=400)
        
        success = state.graph.remove_node(node)
        if not success:
            return JsonResponse({"success": False, "error": "Can not delete node."})

        visualizer = state.visualizers[0]
        html_snippet = visualizer.visualize(state.graph, request)
        state.load_tree()
        tree_html = generate_tree_html(state.tree.roots)

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

    graph = state.graph
    if request.method == "POST":
        data = json.loads(request.body)
        origin = data.get("origin")
        target = data.get("target")
        relation = data.get("relation")

        try:
            
            success = graph.remove_edge(origin, target, relation)
            if not success:
                return JsonResponse({"success": False, "error": "Edge not found"})

            visualizer = state.visualizers[0]
            html_snippet = visualizer.visualize(graph, request)
            state.load_tree()
            tree_html = generate_tree_html(state.tree.roots)

            return JsonResponse({
                "success": True,
                "view_html": html_snippet,
                "tree_html": tree_html
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"success": False, "error": str(e)})

def edit_edge(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            origin_id = data.get("origin")
            old_relation = data.get("old_relation")
            target_id = data.get("target")
            new_relation = data.get("new_relation")

            if not all([origin_id, old_relation, target_id, new_relation]):
                return JsonResponse({"success": False, "error": "Missing data."})

            print(origin_id)
            print(old_relation)
            print(target_id)
            print(new_relation)

            edge = state.graph.get_edge(origin_id, target_id)
            state.graph.remove_edge(origin_id, target_id, old_relation)
            edge.relation = new_relation
            state.graph.insert_edge(edge)
            visualizer = state.visualizers[0]
            html_snippet = visualizer.visualize(state.graph, request)
            state.load_tree()
            tree_html = generate_tree_html(state.tree.roots)

            return JsonResponse({
                "success": True,
                "view_html": html_snippet,
                "tree_html": tree_html
            })

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Only POST allowed'})

def edit_node(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            node_id = data.get('id')
            properties = data.get('properties', {})

            if not node_id:
                return JsonResponse({'success': False, 'error': 'Node ID is required'})
            
            if not isinstance(properties, dict) or len(properties) != 1:
                return JsonResponse({'success': False, 'error': 'Exactly one property must be provided'})
            node = state.graph.get_node(node_id)
            if not node:
                return JsonResponse({'success': False, 'error': 'Node not found'})
            key, value = next(iter(properties.items()))
            success = state.graph.update_node(node, key, value)
            if not success:
                return JsonResponse({"success": False, "error": "Can not edit node."})

            visualizer = state.visualizers[0]
            html_snippet = visualizer.visualize(state.graph, request)
            state.load_tree()
            tree_html = generate_tree_html(state.tree.roots)

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

    old_graph = state.graph
    if old_graph is None:
        return JsonResponse({"success": False, "error": "No graph loaded"}, status=400)

    new_graph = Graph()

    for node in old_graph.get_nodes():
        search_node(new_graph, old_graph, node, query)

    # ažuriranje aplikacije sa novim grafom
    state.graph = new_graph
    state.load_tree()

    return JsonResponse({"success": True})


def search_node(new_graph, old_graph, node, query):
    query = query.strip().lower()
    found = False

    for key, value in node.attributes.items():
        if query in str(key).lower() or query in str(value).lower():
            found = True
            break

    if query in str(node.id).lower():
        found = True

    if found:
        # Dodaj originalni čvor u novi graf
        if not new_graph.has_node(node):
            new_node = copy_node(node)
            new_graph.insert_node(new_node)
        else:
            new_node = new_graph.get_node(node.id)

        # Dodaj sve izlazne grane i povezane čvorove
        for edge in node.edges:
            other = edge.target
            # Dodaj target čvor ako ga nema
            if not new_graph.has_node(other):
                new_other = copy_node(other)
                new_graph.insert_node(new_other)
            else:
                new_other = new_graph.get_node(other.id)

            # Dodaj granu
            new_edge = Edge(origin=new_node, target=new_other, relation=edge.relation, weight=edge.weight, directed=edge.is_directed)
            new_node.add_edge(new_edge)

        # (opciono) Dodaj i sve ulazne grane iz starog grafa
        for edge in old_graph.get_edges():
            if edge.target.id == node.id:
                origin = edge.origin
                if not new_graph.has_node(origin):
                    new_origin = copy_node(origin)
                    new_graph.insert_node(new_origin)
                else:
                    new_origin = new_graph.get_node(origin.id)

                if not new_graph.has_node(node):
                    new_node = copy_node(node)
                    new_graph.insert_node(new_node)

                new_edge = Edge(origin=new_origin, target=new_node, relation=edge.relation, weight=edge.weight, directed=edge.is_directed)
                new_origin.add_edge(new_edge)

def copy_node(original_node):
    new_node = Node(original_node.id)
    for key, value in original_node.attributes.items():
        new_node.add_attribute(key, value)
    return new_node

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
        state.graph = None
        state.base_graph = None
        state.tree = None
        state.current_visualizer = None
        
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

    old_graph = state.graph
    if old_graph is None:
        return JsonResponse({"success": False, "error": "No graph loaded"}, status=400)

    # match = re.match(r"(\w+)\s*(==|=|!=|<=|>=|<|>)\s*['\"]?([\w\s\.\-]+)['\"]?", condition)
    match = re.match(r"([^\s]+)\s*(==|=|!=|<=|>=|<|>)\s*['\"]?(.+?)['\"]?$", condition)

    if not match:
        return JsonResponse({"success": False, "error": "Invalid filter format"}, status=400)

    key, operator, value = match.groups()

    if re.match(r"^-?\d+\.\d+$", value): 
        value = float(value)
    elif re.match(r"^-?\d+$", value):
        value = int(value)

    def match_condition(props):
        if not props:
            return False
        node_val = props.get(key)
        if node_val is None:
            return False

        try:
            if isinstance(value, (int, float)):
                if isinstance(node_val, str) and re.match(r"^-?\d+(\.\d+)?$", node_val):
                    node_val = float(node_val) if '.' in node_val else int(node_val)

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

    # Pronađi čvorove koji zadovoljavaju uslov
    matched_nodes = []
    for node in old_graph.get_nodes():
        if match_condition(node.get_attributes()):
            matched_nodes.append(node)

    # Dodaj čvorove, njihove povezane čvorove i grane
    for node in matched_nodes:
        if not new_graph.has_node(node):
            new_node = copy_node(node)
            new_graph.insert_node(new_node)
        else:
            new_node = new_graph.get_node(node.id)

        # Izlazne grane (target)
        for edge in node.edges:
            target = edge.target
            if not new_graph.has_node(target):
                new_target = copy_node(target)
                new_graph.insert_node(new_target)
            else:
                new_target = new_graph.get_node(target.id)

            new_edge = Edge(origin=new_node, target=new_target, relation=edge.relation, weight=edge.weight, directed=edge.is_directed)
            new_node.add_edge(new_edge)

        # Ulazne grane (origin → ovaj čvor)
        for edge in old_graph.get_edges():
            if edge.target.id == node.id:
                origin = edge.origin
                if not new_graph.has_node(origin):
                    new_origin = copy_node(origin)
                    new_graph.insert_node(new_origin)
                else:
                    new_origin = new_graph.get_node(origin.id)

                new_edge = Edge(origin=new_origin, target=new_node, relation=edge.relation, weight=edge.weight, directed=edge.is_directed)
                new_origin.add_edge(new_edge)

    # Ažuriraj aktivni graf
    state.graph = new_graph
    state.load_tree()

    return JsonResponse({"success": True})


def reset_graph(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    state.graph = state.base_graph
    
    state.load_tree()

    return JsonResponse({"success": True})


def add_workspace(request):
    if not state.graph:
        return JsonResponse({"error": "No graph loaded"}, status=400)
    if not state.visualizer:
        return JsonResponse({"error": "No visualizer selected"}, status=400)
    if not state.loader:
        return JsonResponse({"error": "No loader used"}, status=400)

    ws_id = str(uuid.uuid4())[:8]

    state.workspaces[ws_id] = {
        "graph": state.graph,
        "base_graph": state.base_graph,
        "tree": state.tree,
        "visualizer": state.visualizer,
        "loader": state.loader
    }
    state.current_workspace = ws_id
    return JsonResponse({"success": True, "workspace_id": ws_id})

def switch_workspace(request, ws_id):
    success = state.switch_workspace(ws_id)
    if not success:
        return JsonResponse({"error": "Workspace not found"}, status=404)

    state.load_tree()
    return redirect(f"/visualize?visualizer={state.visualizer.identifier()}")
