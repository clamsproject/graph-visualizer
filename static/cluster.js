let numClusters = 4;
let clusterSummaries = null;

$(".clusterButton").click(function () {
    if ($(this).hasClass("unclustered")) {
        $(this).removeClass("unclustered");
        $(this).addClass("clustered");
        $(this).text("Uncluster");
        $("#clusterExplanationButton").removeClass("inactive");
        cluster();
    } else {
        $(this).removeClass("clustered");
        $(this).addClass("unclustered");
        $(this).text("Cluster");
        if (!$("#clusterExplanationButton").hasClass("inactive"))
            $("#clusterExplanationButton").addClass("inactive");
        uncluster();
    }
});

function cluster() {
    $(".clusterButton").addClass("is-loading");
    $(".topicModelButton").addClass("is-static");
    fetch("/cluster", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({nodes: nodes})
    })
        .then(response => response.json())
        .then(data => {
            $(".clusterButton").removeClass("is-loading");
            $("#clusterColorBox").removeAttr("disabled");
            hideProgressBar();
            nodes = data;
            clusterColors = getRandomColors(numClusters);
            // clusterColors = ['#E3170A', '#A9E5BB', '#B38CB4', '#F7B32B']
            updateGraph();
        })
}

function uncluster() {
    $("#clusterColorBox").attr("disabled", true);
    $(".topicModelButton").removeClass("is-static");
    svg.selectAll(".topicLabel").remove();

    nodes.forEach(node => {
        node.cluster = null;
    });
    clusterSummaries = null;
    updateGraph();
    tick();
}

function argMax(arr) {
    return arr.map((x, i) => [x, i]).reduce((r, a) => (a[0] > r[0] ? a : r))[1];
}

let clusterColors = [];
let topics;

function showClusterExplanations() {
    // showProgressBar();
    $("#clusterExplanationButton").addClass("is-loading")
    nodeCopy = [ ...nodes ];
    nodeCopy = nodeCopy.map(d => {
        return {
                id: d.id,
                summary: d.summary,
                cluster: d.cluster
               }
    })
    fetch("/summarize_clusters", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({nodes: nodeCopy})
    })
    .then(response => response.json())
    .then(data => {
        // showClusterExplanationsModal(data);
        clusterSummaries = data;
        updateGraph();
        // hideProgressBar();
        if (!$("#clusterExplanationButton").hasClass("inactive"))
            $("#clusterExplanationButton").addClass("inactive");
        if ($("#returnButton").hasClass("is-loading"))
            $("#returnButton").removeClass("is-loading");
    })
}



const clusterCenterHTML = `
    <div class="cluster-center">Cluster center</div>
`


function renderClusters(numClusters) {

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

        const occupiedClusters = nodes.map(d => d.hidden ? null : d.cluster);

        clusterCenters = clusterNode.append('g');


        clusterCenters.append('rect')
          .attr('width', d => topics["names"][d.cluster].length * 9 + 20)
          .attr('height', 30)
          .attr('fill', d => clusterColors[d.cluster])
          .attr('x', d => -((topics["names"][d.cluster].length * 9 + 20) / 2))
          .attr('y', -15)
          .attr('visibility', d => occupiedClusters.includes(d.cluster) ? 'visible' : 'hidden')
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
          .attr('visibility', d => occupiedClusters.includes(d.cluster) ? 'visible' : 'hidden')
          .text(d => topics["names"][d.cluster]);
              
    }
    
    else if (clusterSummaries) {
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

            createSummaryTooltip(selectedCluster, clusterSummaries[d["cluster"]], event); // Pass the node selection, data, and event
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

