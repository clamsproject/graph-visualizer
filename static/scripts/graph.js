let clickedNode = null;
let nodes = [];
let frozen = false;

// Fetching nodes is wrapped in a promise so other scripts can wait
// for nodes to be populated (filter-panel especially)
const nodesPromise = new Promise((resolve, reject) => {
    fetch('/all-nodes')
      .then(response => response.json())
      .then(data => {
        nodes = data;
        updateGraph();
        resolve(); // Resolve the Promise when nodes are fetched
      })
      .catch(error => {
        reject(error); // Reject the Promise if there's an error
      });
  });
  
// Set up the dimensions and margins of the graph
const page_width = window.innerWidth;
const page_height = window.innerHeight;
const width = page_width;
const height = page_height;

let zoomBehavior = d3.zoom().on('zoom', zoomed);

// Create the SVG container
const svg = d3.select('#graphWrapper')
  .append('svg')
  .attr('width', width)
  .attr('height', height)
  .call(zoomBehavior)
  .append('g');

const colorScale = d3.scaleLinear()
    .domain([0, 1])
    .range(['#eeeeee', '#152238'])
    .clamp(true);

let links;
let link;

let maxWeight = 0;

function setLinks(manualLinks = null) {
    links = []
    if (!manualLinks) {
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const sharedEntities = nodes[i].entities.slice(0,300).filter(entity => nodes[j].entities.includes(entity));
                weight = ((sharedEntities.length*2)/(nodes[i].entities.length + nodes[j].entities.length))
                if (weight * 100 > maxWeight) maxWeight = weight * 100;
                if (weight*100 >= entitySlider.value && nodes[i].hidden == false && nodes[j].hidden == false) {
                    links.push({ source: nodes[i].id, 
                                 target: nodes[j].id, 
                                 weight: weight, 
                                 sharedEntities: sharedEntities });
                }
            }
        }    
    }
    else links = manualLinks;

    link = svg.selectAll('.link')
        .data(links)
        .enter()
        .append('line')
        .attr('class', 'link')
        .attr('stroke-width', d => (d.weight * (nodeRadius/2)) || 1) // Max stroke width should be node radius
        .attr('stroke', d => colorScale(d.weight*1)); // Set stroke color based on weight
}

setLinks();

const nodeRadius = 15; // Adjust the radius of the circles

let node;
let topicMode = false;

function setNodes() {
    $(".node").remove();
    $(".mmif-filename").remove();
    $(".tooltip").remove(); // Remove existing tooltips
    $(".clusterSummary").remove();

    // Add the nodes as SVG circles and text
    node = svg.selectAll('.node')
        .data(nodes.filter(d => !d.hidden))
        .enter()
        .append('g') // Use a group to hold the circle, text, and tooltip
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragged)
            .on('end', dragEnded));    

    const circles = node.append('circle')
        .attr('class', d => `node ${d.temp ? 'temp loading' : ''}`)
        .attr('r', nodeRadius)
        // .attr('fill', d => 'cluster' in d ? clusterColors[d.cluster] : 'black');

    node.append('text')
        .attr('class', 'mmif-filename')
        .attr('dx', 20) // Offset the text horizontally from the circle
        .style('text-anchor', 'start') // Anchor the text at the start (left side)
        .attr('dy', '.3em') // Offset the text vertically from the circle
        .text(d => d.label) // Set the text content  
        .style('display', filenameCheckbox.checked ? "block" : "none");  

    circles.on('click', (event, d) => {
        const selectedCircle = d3.select(event.target);
        if (clickedNode === d) {
            // If the same node is clicked again, toggle the tooltip
            selectedCircle.classed('clicked', false);
            nodeGroup = node.filter(data => data.id === d.id);
            nodeGroup.select('.tooltip').remove();
            // Lowering nodes in topic modeling mode breaks the chart
            if (!topicMode) {
                nodeGroup.lower();
                link.lower();
                clusterLink.lower();    
            }
            clickedNode = null; // Reset the clicked node
        } else {
            selectedCircle.classed('clicked', true);
            clickedNode = d; // Store the clicked node
            createTooltip(node, d, event); // Pass the node selection, data, and event
        }
    });

    return node
}

function deleteNode(nodeId) {
    fetch('/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'id': nodeId }),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            nodes = nodes.filter(node => node.id !== nodeId);
            updateGraph();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function visualizeNode(nodeId) {
    let mmif_file;
    fetch('/visualize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'id': nodeId }),
    })
        .then(response => response.json())
        .then(data => {
            data = data["res"];
            const idPrefix = "Visualization ID is ";
            const startIndex = data.indexOf(idPrefix) + idPrefix.length;
            const endIndex = data.indexOf("\n", startIndex);
            const id = data.slice(startIndex, endIndex);
            window.open(`http://localhost:5000/display/${id}`, '_blank');
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

setNodes();

let simulation;

function setSimulation() {
    // stop the simulation if it's already running
    if (!simulation) {
        simulation = d3.forceSimulation();
    }
    
    // Create the simulation
    simulation
        .nodes(nodes)
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force("charge", d3.forceManyBody().strength(-1000))
        // .force("link", d3.forceLink(links).id(d => d.id).distance(width * 0.15).strength(2))
        .force("link", d3.forceLink(links).id(d => d.id).distance(d => (1/(d.weight/100) + (width * 0.05))).strength(1))
        .force("x", d3.forceX().strength(0.1))
        .force("y", d3.forceY().strength(0.1))
        .on("tick", tick);
}

setSimulation();


let hasBeenDragged = false;
let clusterCenters = null;
let clusterLink = null;
// Drag functions
function dragStarted(event, d) {
    // if (!event.active) simulation.alphaTarget(0.3).restart();
    // d.fx = d.x;
    // d.fy = d.y;
}

function dragged(event, d) {
    // Resume sim alpha target if dragged. This needs to be here rather than
    // in dragStarted so the simulation doesn't resume when clicking a node.
    if (frozen) return;
    if (hasBeenDragged == false) {
        simulation.alphaTarget(0.3).restart();
        hasBeenDragged = true;
    }
    d.fx = event.x;
    d.fy = event.y;
}

function dragEnded(event, d) {
    if (frozen) return;
    if (!event.active) simulation.alphaTarget(0);
    // if (!hasBeenDragged) simulation.force(0);
    hasBeenDragged = false;
    d.fx = null;
    d.fy = null;
}

let topicBackground;
// Update node and link positions on each tick of the simulation
function tick() {

    // Highlight/gray out nodes if pie slice is chosen
    if (hoveredCLAMSApp != null) {
        resetNodes();
        // Set the fill color of nodes you want to gray out
        node.filter(d => !d.apps.some(app => app === hoveredCLAMSApp))
            .select('circle')
            .style('opacity', 0.2);
    } else if (hoveredEntity != null) {
        resetNodes();
        node.filter(d => !(d.entities.includes(hoveredEntity)))
            .select('circle')
            .style('opacity', 0.2);
    } else {
        resetNodes();
    }

    if (frozen) {
        node.select('circle')
            .style('visibility', d => d.hidden ? 'hidden' : 'visible');
        return;
    }
    
    link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

    if (clusterLink) {
        clusterLink
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
    }

    // Update the position of circles
    node
        .attr('cx', d => d.x) // Set the 'cx' attribute for the x-coordinate of the circle
        .attr('cy', d => d.y) // Set the 'cy' attribute for the y-coordinate of the circle
        .attr('transform', d => `translate(${d.x}, ${d.y})`);

    if (clusterCenters) {
        clusterCenters
            .attr('cx', d => d.x)
            .attr('cy', d => d.y)
            .attr('transform', d => `translate(${d.x}, ${d.y})`);
    }    
}

function resetNodes() {
    node.select('circle')
        .style('opacity', 1);
}

function zoomed({ transform }) {
    svg.attr('transform', transform);
    //   Text should disappear if zoomed out far enough
    if (transform.k < 0.75) {
        if (filenameCheckbox.checked) node.selectAll('text').style('display', 'none');
        // node.selectAll('.tooltip').style('display', 'none');
    }
    else {
        if (filenameCheckbox.checked) node.selectAll('text').style('display', 'block');
        // node.selectAll('.tooltip').style('display', 'block');
    }
}

function updateGraph(manualLinks=null) {
    svg.selectAll("line").remove();
    svg.selectAll("rect").remove();
    svg.selectAll("foreignObject").remove();
    svg.selectAll("text").remove();
    frozen = false;
    console.log("Setting links...")
    setLinks(manualLinks);
    // setLinkOverlays();
    console.log("Setting nodes...")
    setNodes();

    console.log("Setting simulation...")
    setSimulation();

    setNodeColors(clusterColorCheckbox.checked);

    console.log("Rendering clusters...")
    renderClusters(numClusters);
    console.log("Done.")
}

function addNode(new_node) {
    const parsedNode = JSON.parse(new_node);
    const existingNode = nodes.find(node => node.id === parsedNode.id);
    if (existingNode) {
        Object.assign(existingNode, parsedNode);
    } else {
        nodes = nodes.concat(parsedNode);
    }

    updateGraph();
}

function addTempFile(filename) {
    filename = filename.replace(".mmif", "").replace(".json", "");
    new_node = { 'id': filename, 
                 'label': filename, 'apps': [], 
                 'summary': "Generating summary...", 
                 'entities': [], 
                 'temp': true }
    addNode(JSON.stringify([new_node]));
}

function setNodeColors(colorsEnabled) {
    if (!colorsEnabled) {
        node.selectAll('circle').attr('fill', 'black');
    }
    else {
        node.selectAll('circle').attr('fill', d => 'cluster' in d ? clusterColors[d.cluster] : 'black');
    }
}