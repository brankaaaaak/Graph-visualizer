import json
from django.template import engines
from api.services.visualizer import BaseVisualizer


class SimpleVisualizer(BaseVisualizer):
    def identifier(self):
        return "simple-visualizer"

    def name(self):
        return "Simple View"
    
    def visualize(self, graph, request):
        nodes = {}
        for node in graph.nodes:
            attributes = [f"{key}: {value}" for key, value in node.attributes.items()]
            nodes[node.id] = {"id": "id-" + str(node.id), "attributes": attributes}
            
        connections = []
        for edge in graph.get_edges():
            connection = {"source": edge.origin.id, "target": edge.target.id}
            connections.append(connection)
        print(nodes)
        print(connections)
        view = """
        <style>
        .node {
            color: #f3eee9;
            cursor: pointer;
            text-align: center;
        }

        .connection {
            stroke: #3c2956;
            fill: none;
            stroke-width: 2px;
        }
        </style>
        <script type="text/javascript">
        $(document).ready(function () {
            var selected_node = null;
            var connections = JSON.parse("{{connections |escapejs}}");
            var nodes = JSON.parse("{{nodes |escapejs}}");

            var width = 900;
            var height = 400;

            connections.forEach(function (connection) {
                connection.source = nodes[connection.source];
                connection.target = nodes[connection.target];
            });

            var force = d3.layout.force()
                .size([width, height])
                .nodes(d3.values(nodes))
                .links(connections)
                .on("tick", tick)
                .linkDistance(300)
                .charge(-300)
                .gravity(0.5);
                
            d3.select("#main-view svg").remove();
            var svg = d3.select("#main-view")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g");

            var connection = svg.selectAll('.connection')
                .data(connections)
                .enter().append('line')
                .attr('class', 'connection');

            var node = svg.selectAll('.node')
                .data(force.nodes())
                .enter().append('g')
                .attr('class', 'node')
                .attr('id', function (d) { return d.id; })
                .on('click', function () {
                    nodeClick(this);
                });

            d3.selectAll('.node').each(function (d) { nodeView(d, '#241f4c'); });

            force.start();

            function nodeView(d, color) {
                var width = 30;
                var textSize = 10;
                d3.select("g#" + d.id).append('circle')
                    .attr('cx', 0).attr('cy', 0).attr('r', width).attr('fill', color);
                d3.select("g#" + d.id).append('text').attr('x', 0).attr('y', 4)
                    .attr('text-anchor', 'middle')
                    .attr('font-size', textSize).attr('font-family', 'poppins')
                    .attr('fill', 'white').text(d.id);
            }

            function tick(e) {
                var radius = 30;  // poluprečnik čvora (kuglice)

                node.each(function(d) {
                    // Ograniči X da ne izađe lijevo ili desno izvan SVG
                    if (d.x < radius) {
                        d.x = radius;
                        d.px = d.x + (d.x - d.px) * -1;  // odbij nazad
                    }
                    if (d.x > width - radius) {
                        d.x = width - radius;
                        d.px = d.x + (d.x - d.px) * -1;
                    }

                    // Ograniči Y da ne izađe gore ili dole izvan SVG
                    if (d.y < radius) {
                        d.y = radius;
                        d.py = d.y + (d.y - d.py) * -1;  // odbij nazad
                    }
                    if (d.y > height - radius) {
                        d.y = height - radius;
                        d.py = d.y + (d.y - d.py) * -1;
                    }
                });
                node.attr("transform", function (d) { return "translate(" + d.x + "," + d.y + ")"; })
                    .call(force.drag);

                connection.attr('x1', function (d) { return d.source.x; })
                    .attr('y1', function (d) { return d.source.y; })
                    .attr('x2', function (d) { return d.target.x; })
                    .attr('y2', function (d) { return d.target.y; });
            }

            function nodeClick(element) {
                var nodeId = element.id.replace("id-", "");

            // Reset prethodnog selektovanog čvora ako postoji
            if (selected_node != null) {
                nodeView(nodes[selected_node.id.replace("id-", "")], "#241f4c");
            }

            var new_node = nodes[nodeId];
            selected_node = new_node;
            nodeView(selected_node, "pink");

            // Prikaži atribute u alert prozoru
            var description = "ID: " + element.id + "\\n";
            for (var i = 0; i < new_node.attributes.length; i++) {
                description += new_node.attributes[i] + "\\n";
            }
            alert(description);

            // Pošalji AJAX zahtjev ka serveru da otvori čvor u stablu preko funkcije expand
            fetch(`/expand/${encodeURIComponent(nodeId)}/`)
                .then(res => {
                    if (!res.ok) throw new Error("Server returned " + res.status);
                    return res.text();
                })
                .then(html => {
                    const treeView = document.getElementById("tree-view");
                    treeView.innerHTML = "<h3>Tree View</h3>" + html;
                    setTimeout(() => {
                        const target = document.querySelector(`[data-node-id="${nodeId}"]`);
                        if (target) {
                            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }, 100);
                })
                .catch(err => {
                    //console.error("Greška pri otvaranju čvora u stablu:", err);
                    //alert("Greška pri otvaranju čvora u stablu: " + err.message);
                });
            }
        });
        </script>
        """
        django_engine = engines['django']
        view_html = django_engine.from_string(view)
        view_html = view_html.render({
            "nodes": json.dumps(nodes),
            "connections": json.dumps(connections)
        }, request)
        return view_html
    
