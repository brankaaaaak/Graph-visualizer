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

            var width = 1000;
            var height = 450;

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
                .charge(-5000)
                .gravity(0.5);

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
                var textSize = 12;
                d3.select("g#" + d.id).append('circle')
                    .attr('cx', 0).attr('cy', 0).attr('r', width).attr('fill', color);
                d3.select("g#" + d.id).append('text').attr('x', 0).attr('y', 4)
                    .attr('text-anchor', 'middle')
                    .attr('font-size', textSize).attr('font-family', 'poppins')
                    .attr('fill', 'white').text(d.id);
            }

            function tick(e) {
                node.attr("transform", function (d) { return "translate(" + d.x + "," + d.y + ")"; })
                    .call(force.drag);

                connection.attr('x1', function (d) { return d.source.x; })
                    .attr('y1', function (d) { return d.source.y; })
                    .attr('x2', function (d) { return d.target.x; })
                    .attr('y2', function (d) { return d.target.y; });
            }

            function nodeClick(element) {
                var description="id:"+element.id+"\\n";
                var id=selected_node.id.replace("id-","");
                if(selected_node!=null){
                    nodeView(nodes[id],"#241f4c");
                }

                var element_id=element.id.replace("id-","");
                var new_node=nodes[element_id];
                selected_node=new_node;

                nodeView(selected_node,"pink")

                for(var i=0;i<new_node.attributes.length;i++) {
                   description += new_node.attributes[i] + "\\n";
                }
                trimmed_id=element.id.replace("id-","");

                alert(description);
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
    
