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
            var currentScale = 1;
            var currentTranslate = [0, 0];

            var selected_node=null;
            var nodesGraph = JSON.parse("{{ nodes|escapejs }}");
            var connectionsGraph = JSON.parse("{{ connections|escapejs }}");

            var width = 900;
            var height = 500;

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
                .charge(-5000)
                .gravity(0.5);

            var svgRoot = d3.select("#main-view")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .call(d3.behavior.zoom().on("zoom", function () {
                    currentScale = d3.event.scale;
                    currentTranslate = d3.event.translate;
                    svg.attr("transform", "translate(" + currentTranslate + ") scale(" + currentScale + ")");
                    drawViewport();
                }));

            var svg = svgRoot.append("g");


            var connection = svg.selectAll(".connection")
                .data(connectionsGraph)
                .enter().append("line")
                .attr("class", "connection");

            var node = svg.selectAll(".node")
                .data(force.nodes())
                .enter().append("g")
                .attr("class", "node")
                .attr("id", function (d) { return d.id; })
                .attr("pointer-events", "all")
                .on("mousedown", function () { d3.event.stopPropagation(); })
                .on("dragstart", function (d) {
                    d.fixed = true;
                })
                .on("click", function () {
                    nodeClick(this);
                })
                .on("mouseover", function (d) {
                    d3.select(this).append("title")
                        .text(d.attributes.join(", "));
                })
                .on("mouseout", function () {
                    d3.select(this).select("title").remove();
                })
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

                var maxAttrTextLength = 30;  

                for (var i = 0; i < d.attributes.length; i++) {
                    var attrText = d.attributes[i];
                    var displayText = attrText.length > maxAttrTextLength
                        ? attrText.substring(0, maxAttrTextLength - 3) + "..."
                        : attrText;

                    g.append("text")
                        .attr("x", 5)
                        .attr("y", 30 + i * textSize)
                        .attr("font-size", textSize)
                        .attr("fill", "white")
                        .text(displayText)
                        .append("title")
                        .text(attrText);  
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
            function nodeView(d, color) {
                var g = d3.select("g#" + d.id);
                g.select("rect").attr("fill", color);
            }

            function nodeClick(element) {
                var nodeId = element.id.replace("id-", "");

                if (selected_node != null) {
                    nodeView(nodesGraph[selected_node.id.replace("id-", "")], "#241f4c");
                }

                var new_node = nodesGraph[nodeId];
                selected_node = new_node;
                nodeView(selected_node, "pink");
                updateBirdView();

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
            function updateBirdView() {
                var mainGroup = d3.select("#main-view svg g");
                if (mainGroup.empty()) return;

                var birdDiv = d3.select("#bird-view");
                birdDiv.select("svg").remove();

                var clonedGroup = mainGroup.node().cloneNode(true);

                var birdSvg = birdDiv.append("svg")
                    .attr("width", birdDiv.node().clientWidth)
                    .attr("height", birdDiv.node().clientHeight);

                birdSvg.node().appendChild(clonedGroup);

                var padding = 10;
                var bbox = clonedGroup.getBBox();

                var birdWidth = birdDiv.node().clientWidth - 2 * padding;
                var birdHeight = birdDiv.node().clientHeight - 2 * padding;

                var scaleWidth = birdWidth / bbox.width;
                var scaleHeight = birdHeight / bbox.height;
                var scale = Math.min(scaleWidth, scaleHeight);

                d3.select(clonedGroup)
                    .attr("transform", `translate(${padding - bbox.x * scale}, ${padding - bbox.y * scale}) scale(${scale})`);

                birdSvg.selectAll("rect").attr("stroke-width", 0.5);
                birdSvg.selectAll("line").attr("stroke-width", 1);
                birdSvg.selectAll("text").attr("font-size", 9);
                drawViewport();

            }

            force.on("end", function () {
                updateBirdView();
            });
            function drawViewport() {
                var birdSvg = d3.select("#bird-view").select("svg");
                var group = birdSvg.select("g");
                if (group.empty()) return;

                var birdBBox = group.node().getBBox();

                var birdWidth = birdSvg.node().clientWidth;
                var birdHeight = birdSvg.node().clientHeight;

                var scaleWidth = (birdWidth - 20) / birdBBox.width;
                var scaleHeight = (birdHeight - 20) / birdBBox.height;
                var scale = Math.min(scaleWidth, scaleHeight);

                var viewWidth = width / currentScale;
                var viewHeight = height / currentScale;
                var x = -currentTranslate[0] / currentScale;
                var y = -currentTranslate[1] / currentScale;

                var viewportX = (x - birdBBox.x) * scale + 10;
                var viewportY = (y - birdBBox.y) * scale + 10;
                var viewportWidth = viewWidth * scale;
                var viewportHeight = viewHeight * scale;

                birdSvg.selectAll(".viewport-rect").remove();

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

                    });
        </script>
        """

        django_engine = engines['django']
        template = django_engine.from_string(view)
        return template.render({
            "nodes": json.dumps(nodes),
            "connections": json.dumps(connections)
        }, request)
