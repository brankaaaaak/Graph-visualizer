import json
from django.template import engines
from api.services.visualizer import BaseVisualizer


class BlockVisualizer(BaseVisualizer):
    def identifier(self):
        return "block-visualizer"

    def name(self):
        return "Block View"
    
    def visualize(self, graph, request):
        nodes = {}
        for node in graph.nodes:
            attributes = [f"{key}: {value}" for key, value in node.attributes.items()]
            nodes[node.id] = {"id": "id-" + str(node.id), "attributes": attributes}

        connections = []
        for edge in graph.get_edges():
            connections.append({"source": edge.origin.id, "target": edge.target.id})

        view = """
        <style>
        .node {
            cursor: pointer;
        }

        .connection {
            stroke: #3c2956;
            fill: none;
            stroke-width: 2px;
        }
        </style>

        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://d3js.org/d3.v3.min.js"></script>

        <script type="text/javascript">
        $(document).ready(function () {
            var nodesGraph = JSON.parse("{{ nodes|escapejs }}");
            var connectionsGraph = JSON.parse("{{ connections|escapejs }}");

            var width = 800;
            var height = 350;

            connectionsGraph.forEach(function (conn) {
                conn.source = nodesGraph[conn.source];
                conn.target = nodesGraph[conn.target];
            });

            var force = d3.layout.force()
                .size([width, height])
                .nodes(d3.values(nodesGraph))
                .links(connectionsGraph)
                .on("tick", tick)
                .linkDistance(300)
                .charge(-2000)
                .gravity(0.5);

            var svg = d3.select("#main-view")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g");

            var connection = svg.selectAll(".connection")
                .data(connectionsGraph)
                .enter().append("line")
                .attr("class", "connection");

            var node = svg.selectAll(".node")
                .data(force.nodes())
                .enter().append("g")
                .attr("class", "node")
                .attr("id", function (d) { return d.id; })
                .call(force.drag);

            node.each(function (d) {
                var g = d3.select(this);
                var textSize = 12;
                var attrHeight = d.attributes.length * textSize;
                var height = 30 + attrHeight;
                var width = 160;

                g.append("rect")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("width", width)
                    .attr("height", height)
                    .attr("fill", "#3c2956");

                g.append("text")
                    .attr("x", width / 2)
                    .attr("y", 15)
                    .attr("text-anchor", "middle")
                    .attr("font-size", textSize)
                    .attr("fill", "white")
                    .text(d.id);

                for (var i = 0; i < d.attributes.length; i++) {
                    g.append("text")
                        .attr("x", 5)
                        .attr("y", 30 + i * textSize)
                        .attr("font-size", textSize)
                        .attr("fill", "white")
                        .text(d.attributes[i]);
                }
            });

            force.start();

            function tick() {
                node.attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y + ")";
                });

                connection.attr("x1", function (d) { return d.source.x; })
                          .attr("y1", function (d) { return d.source.y; })
                          .attr("x2", function (d) { return d.target.x; })
                          .attr("y2", function (d) { return d.target.y; });
            }
        });
        </script>
        """

        django_engine = engines['django']
        template = django_engine.from_string(view)
        return template.render({
            "nodes": json.dumps(nodes),
            "connections": json.dumps(connections)
        }, request)
