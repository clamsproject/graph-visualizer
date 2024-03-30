// let hoveredCLAMSApp = null;
let clickedNode = null;

// Define the data for nodes and links
const nodes = [
    { id: 'node1', label: 'ocr1.mmif', apps: ['doctr-wrapper'], summary: "This is an example summary for ocr1.mmif"},
    { id: 'node2', label: 'swt1.mmif', apps: ['swt-detection', 'doctr-wrapper'], summary: "This is an example summary for swt1.mmif"},
    { id: 'node3', label: 'ner.mmif', apps: ['spacy-wrapper'], summary: "This is an example summary for ner1.mmif"},
    { id: 'node4', label: 'ex.mmif', apps: [], summary: "This is an example summary for ex.mmif" },
    { id: 'node5', label: 'swt-rfb.mmif', apps: ['swt-detection', 'doctr-wrapper', 'role-filler-binder'], summary: "This is an example summary for swt-rfb.mmif" }
];

const links = [
    { source: 'node1', target: 'node2', weight: 3, sharedEntities: ['Pizza Hut', "Papa John's", "Domino's"] },
    { source: 'node2', target: 'node3', weight: 1, sharedEntities: ['United States'] },
    // { source: 'node3', target: 'node4' },
    // { source: 'node4', target: 'node5' },
    { source: 'node5', target: 'node1', weight: 1, sharedEntities: ['Congress'] }
];

// Set up the dimensions and margins of the graph
const page_width = window.innerWidth;
const page_height = window.innerHeight;
const width = page_width;
const height = page_height;

// Create the SVG container
const svg = d3.select('#graphWrapper')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .call(d3.zoom().on('zoom', zoomed))
    .append('g');

const colorScale = d3.scaleLinear()
    .domain([1, 3])
    .range(['#999', '#333'])
    .clamp(true);

// Add the links
const link = svg.selectAll('.link')
    .data(links)
    .enter()
    .append('line')
    .attr('class', 'link')
    .attr('stroke-width', d => d.weight || 1)
    .attr('stroke', d => colorScale(d.weight)); // Set stroke color based on weight

// Add the link overlay
const linkOverlay = svg.selectAll('.linkOverlay')
    .data(links)
    .enter()
    .append('line')
    .attr('class', 'linkOverlay')
    .attr('stroke-width', 25)
    .attr('stroke', 'transparent');

const tooltip = d3.select('body')
    .append('div')
    .attr('class', 'tooltip')
    .style('opacity', 0);

linkOverlay.on('mouseover', function (event, d) {
    tooltip.transition()
        .duration(200)
        .style('opacity', .9);

    const entityHeader = `<h3>Shared Entities</h3>`;
    const sharedEntities = entityHeader + d.sharedEntities.map(line => `<p>${line}</p>`).join('');
    tooltip.html(sharedEntities)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px')
        .style('height', 'auto')
        .style('width', 'auto');
})
    .on('mouseout', function (d) {
        tooltip.transition()
            .duration(500)
            .style('opacity', 0);
    });

const nodeRadius = 15; // Adjust the radius of the circles

// Add the nodes as SVG circles and text
const node = svg.selectAll('.node')
    .data(nodes)
    .enter()
    .append('g') // Use a group to hold the circle and text
    .call(d3.drag()
        .on('start', dragStarted)
        .on('drag', dragged)
        .on('end', dragEnded));

const circles = node.append('circle')
    .attr('class', 'node')
    .attr('r', nodeRadius);

node.append('text')
    .attr('class', 'mmif-filename')
    .attr('dx', 20) // Offset the text horizontally from the circle
    .style('text-anchor', 'start') // Anchor the text at the start (left side)
    .attr('dy', '.3em') // Offset the text vertically from the circle
    .text(d => d.label); // Set the text content

// Add click event listener to links
circles.on('click', (event, d) => {
    event.stopPropagation();
    updatePanel(d.id);
});


// Create the simulation
const simulation = d3.forceSimulation()
    .nodes(nodes)
    .force("charge", d3.forceManyBody().strength(-1000))
    .force('center', d3.forceCenter(width / 2, height / 2).strength(1))
    .force("link", d3.forceLink(links).id(d => d.id).distance(width * 0.15).strength(1))
    .force("x", d3.forceX().strength(0.1))
    .force("y", d3.forceY().strength(0.1))
    .on("tick", tick);

// Drag functions
function dragStarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragEnded(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Update node and link positions on each tick of the simulation
function tick() {
    link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

    linkOverlay
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);


    // Update the position of circles
    node
        .attr('cx', d => d.x) // Set the 'cx' attribute for the x-coordinate of the circle
        .attr('cy', d => d.y) // Set the 'cy' attribute for the y-coordinate of the circle
        .attr('transform', d => `translate(${d.x}, ${d.y})`);

    // Highlight/gray out nodes if pie slice is chosen
    chosenCLAMSApps = clickedCLAMSApps.map(id => labels[id]) + [hoveredCLAMSApp];
    if (chosenCLAMSApps != []) {
        resetNodes();
        // Set the fill color of nodes you want to gray out
        node.filter(d => !d.apps.some(app => chosenCLAMSApps.includes(app)))
            .select('circle')
            .style('opacity', 0.2);
    } else {
        resetNodes();
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
        node.selectAll('text').style('display', 'none');
    }
    else {
        node.selectAll('text').style('display', 'block');
    }
}