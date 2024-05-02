
const clusterCenterHTML = `
    <div class="cluster-center">Cluster center</div>
`


function renderClusters(numClusters, summaries=null) {

    clusterLinks = [];
    clusterNodes = [];
    for (let i = 0; i < numClusters; i++) {
        clusterNodes.push({id: `cluster-${i}`, label: `Cluster ${i}`, cluster: i, weight: 0, temp: false});
    }
    clusterLinks = []
    for (let i = 0; i < nodes.length; i++) {
        for (let j = 0; j < numClusters; j++) {
            if (nodes[i].hidden) continue;
            if (nodes[i]["cluster"] == clusterNodes[j]["cluster"]) {
                clusterLinks.push({source: nodes[i].id, target: clusterNodes[j].id, weight: null, cluster: clusterNodes[j]["cluster"]});
            }
        }
    }    

    clusterLink = svg.selectAll('.clusterLink')
        .data(clusterLinks)
        .enter()
        .append('line')
        .attr('class', 'link')
        .attr('stroke-width', d => 2)
        .attr('stroke', d => clusterColors[d.cluster])
        // .sttr('stroke-opacity', 0.5)
        .lower();

    // Add the nodes as SVG circles and text
    clusterNode = svg.selectAll('.nodeCluster')
        .data(clusterNodes)
        .enter()
        .append('g') // Use a group to hold the circle, text, and tooltip
        .raise()
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragged)
            .on('end', dragEnded));

    if (topics) {
        clusterCenters = clusterNode.append('g');

        clusterCenters.append('rect')
          .attr('width', d => topics["names"][d.cluster].length * 9 + 20)
          .attr('height', 30)
          .attr('fill', d => clusterColors[d.cluster])
          .attr('x', d => -((topics["names"][d.cluster].length * 9 + 20) / 2))
          .attr('y', -15)
          .attr('class', 'topicLabel');

        clusterCenters.append('text')
          .attr('class', 'mmif-filename')
          .attr('x', 0)
          .attr('y', 5)
          .attr('font-size', 12)
          .attr('font-family', 'sans-serif')
          .attr('text-anchor', 'middle')
          .attr('fill', 'black')
          .attr('class', 'topicLabel')
          .text(d => topics["names"][d.cluster]);

              
    // clusterCenters.append('xhtml:div')
    //     .attr('class', 'card')
    //     .style('width', `0`)
    //     .style('height', `0`)
    //     .html(clusterCenterHTML);
    }
    else if (summaries) {
        clusterCenters = clusterNode.append('g')
            .attr('class', 'clusterSummary');

        clusterCenters.append('circle')
            .attr('r', nodeRadius/2)
            .attr('fill', 'white')
            .attr('stroke', d => clusterColors[d.cluster])
            .append('text')
            .attr('x', 0)
            .attr('y', 0)
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'middle')
            .attr('fill', 'black')
            .text('?');

        clusterCenters.on('click', (event, d) => {
            const selectedCircle = d3.select(event.target);
            const selectedCluster = selectedCircle.select(function() {
                return this.parentNode;
            });
            // if (clickedNode === d) {
            //     // If the same node is clicked again, toggle the tooltip
            //     selectedCircle.classed('clicked', false);
            //     nodeGroup = node.filter(data => data.id === d.id);
            //     nodeGroup.select('.tooltip').remove();
            //     // Lowering nodes in topic modeling mode breaks the chart
            //     if (!topicMode) {
            //         nodeGroup.lower();
            //         link.lower();
            //         clusterLink.lower();    
            //     }
            //     clickedNode = null; // Reset the clicked node
            // } else {
                // selectedCircle.classed('clicked', true);
                // clickedNode = d; // Store the clicked node
                createSummaryTooltip(selectedCluster, summaries[d["cluster"]], event); // Pass the node selection, data, and event
            // }
        });
        

    }
    
    else {
    clusterCenters = clusterNode.append('foreignObject')
        .attr('width', 0)
        .attr('height', 0);

    clusterCenters.append('xhtml:div')
        .attr('class', 'card')
        .style('width', `0`)
        .style('height', `0`)
        .html(clusterCenterHTML);

    }

    // Add cluster centers to simulation
    simulation.nodes(nodes.concat(clusterNodes));
    simulation.force("link", d3.forceLink(clusterLinks.concat(links))
                            .id(d => d.id)
                            .strength(d => d.weight == null ? 1 : 0.05));

    simulation.alpha(1).restart(); // Restart the simulation
}

// function add

function getRandomColors(n) {
    var colors = [];
    for (var i = 0; i < n; i++) {
        colors.push(randomColor());
    }
    return colors;
}

const randomColor = (() => {
    "use strict";
  
    const randomInt = (min, max) => {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    };
  
    return () => {
      var h = randomInt(0, 360);
      var s = randomInt(42, 98);
      var l = randomInt(40, 90);
      return `hsl(${h},${s}%,${l}%)`;
    };
  })();

