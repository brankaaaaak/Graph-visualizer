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
            var currentScale = 1;
            var currentTranslate = [0, 0];

            var selected_node = null;
            var connections = JSON.parse("{{connections |escapejs}}");
            var nodes = JSON.parse("{{nodes |escapejs}}");

            var width = 900;
            var height = 500;

            connections.forEach(function (connection) {
                connection.source = nodes[connection.source];
                connection.target = nodes[connection.target];
            });

            var force = d3.layout.force()
                .size([width, height])
                .nodes(d3.values(nodes))
                .links(connections)
                .on("tick", tick)
                .linkDistance(150)
                .charge(-5000)
                .gravity(0.5);
                
            d3.select("#main-view svg").remove();
            var svgRoot = d3.select("#main-view")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .call(d3.behavior.zoom().on("zoom", function () {
                    currentScale = d3.event.scale;
                    currentTranslate = d3.event.translate;
                    svg.attr("transform", "translate(" + currentTranslate + ") scale(" + currentScale + ")");
                    drawViewport(); 
                }))

                .append("g");

            var svg = svgRoot;


            var connection = svg.selectAll('.connection')
                .data(connections)
                .enter().append('line')
                .attr('class', 'connection');

            var node = svg.selectAll('.node')
                .data(force.nodes())
                .enter().append('g')
                .attr('class', 'node')
                .attr('id', function (d) { return d.id; })
                .attr("pointer-events", "all")
                .on("mousedown", function() { d3.event.stopPropagation(); })
                .on("click", function () {
                    nodeClick(this);
                })
                .on("dragstart", function (d) {
                    d.fixed = true;
                })
                .on("mouseover", function (d) {
                    d3.select(this).append("title")
                        .text(d.attributes.join(", "));
                })
                .on("mouseout", function () {
                    d3.select(this).select("title").remove();
                })
                .call(force.drag);


            d3.selectAll('.node').each(function (d) { nodeView(d, '#241f4c'); });

            force.start();
            function updateBirdView() {
                let mainGroup = d3.select("#main-view svg g");
                if (mainGroup.empty()) return;  // ako nema SVG
                let padding = 20;
                let birdDiv = d3.select("#bird-view");

                birdDiv.select("svg").remove();

                let clonedGroup = mainGroup.node().cloneNode(true);

                let birdSvg = birdDiv.append("svg")
                    .attr("width", birdDiv.node().clientWidth)
                    .attr("height", birdDiv.node().clientHeight);

                birdSvg.node().appendChild(clonedGroup);

                let bbox = clonedGroup.getBBox();

                let birdWidth = birdDiv.node().clientWidth - 2 * padding;
                let birdHeight = birdDiv.node().clientHeight - 2 * padding;


                let scaleWidth = birdWidth / bbox.width;
                let scaleHeight = birdHeight / bbox.height;
                let scale = Math.min(scaleWidth, scaleHeight);

                d3.select(clonedGroup)
                    .attr("class", "bird-group")
                    .attr("transform", `translate(${padding - bbox.x * scale}, ${padding - bbox.y * scale}) scale(${scale})`);


                birdSvg.selectAll("circle").attr("r", 40);
                birdSvg.selectAll("text").attr("font-size", 11);

                birdSvg.selectAll("line").attr("stroke-width", 0.9);
                drawViewport();
            }

            force.on("end", function() {
                updateBirdView();
            });
            function drawViewport() {
                let birdSvg = d3.select("#bird-view").select("svg");
                let group = birdSvg.select("g");
                if (group.empty()) return;

                let birdBBox = group.node().getBBox();

                let birdWidth = birdSvg.node().clientWidth;
                let birdHeight = birdSvg.node().clientHeight;

                let scaleWidth = (birdWidth - 40) / birdBBox.width;
                let scaleHeight = (birdHeight - 40) / birdBBox.height;
                let scale = Math.min(scaleWidth, scaleHeight);

                // Pozicija i dimenzije viewporta u bird view koordinatama
                let viewWidth = width / currentScale;
                let viewHeight = height / currentScale;
                let x = -currentTranslate[0] / currentScale;
                let y = -currentTranslate[1] / currentScale;

                let viewportX = (x - birdBBox.x) * scale + 20;
                let viewportY = (y - birdBBox.y) * scale + 20;
                let viewportWidth = viewWidth * scale;
                let viewportHeight = viewHeight * scale;

                // Ukloni prethodni viewport ako postoji
                birdSvg.selectAll(".viewport-rect").remove();

                // Dodaj novi
                birdSvg.append("rect")
                    .attr("class", "viewport-rect")
                    .attr("x", viewportX)
                    .attr("y", viewportY)
                    .attr("width", viewportWidth)
                    .attr("height", viewportHeight)
                    .attr("stroke", "red")
                    .attr("fill", "none")
                    .attr("stroke-width", 2);
            }



            function nodeView(d, color) {
                var width = 40;
                var textSize = 15;
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
                    const prevSelected = treeView.querySelector(".selected-node");
                    if (prevSelected) {
                        prevSelected.classList.remove("selected-node");
                    }
                    setTimeout(() => {
                        const target = treeView.querySelector(`[data-graph-node-id="${nodeId}"]`);
                        if (target) {
                            target.classList.add("selected-node");
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
    
