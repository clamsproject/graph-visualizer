function mostCommon(arr, n) {
    nMostCommon = []
    for (var i = 0; i < arr.length; i++) {
        if (!nMostCommon.includes(arr[i])) {
            nMostCommon.push(arr[i]);
        }
        if (nMostCommon.length >= n) {
            return nMostCommon;
        }
    }
    return nMostCommon;
}

// TODO: Highlight shared entities
function createTooltip(nodeSelection, d, event) {
    const tooltipWidth = 300;
    const tooltipHeight = 400;

    // Remove existing tooltip for the clicked node
    nodeSelection.filter(data => data.id === d.id).select('.tooltip').remove();

    const nodeGroup = nodeSelection.filter(data => data.id === d.id);

    // Create a new group for the tooltip
    const tooltipGroup = nodeGroup
        .append('g')
        .attr('class', 'tooltip')
        .call(d3.drag() // Add the drag behavior to the tooltip group
            .on('start', dragStartedTooltip)
            .on('drag', draggedTooltip)
            .on('end', dragEndedTooltip));

    // Create a foreignObject to hold the HTML content
    const foreignObject = tooltipGroup.append('foreignObject')
        .attr('x', 20) // Offset from the node circle
        .attr('y', -20) // Offset from the node circle
        .attr('width', tooltipWidth)
        .attr('height', tooltipHeight)
        .style('z-index', '1000');

    // Append an HTML div within the foreignObject
    const div = foreignObject.append('xhtml:div')
        .attr('class', 'card')
        .style('width', `${tooltipWidth}px`);
        // .style('height', '500px');

    entityTags = "";
    // First 10 entities in list are most common entities
    mostCommonEntities = mostCommon(d.entities, 10)
    mostCommonEntities.forEach(entity => entityTags = entityTags.concat(`<span class="entitytag tag is-primary">${entity}</span>`));
    div.html(`
        <header class="card-header tooltip-header">
            <p class="card-header-title">${d.label}</p>
            <button class="card-header-icon" aria-label="more options">
                <span class="icon">
                    <i class="fa-solid fa-close tooltip-close"></i>
                </span>
            </button>
        </header>
        <div class="card-content card-summary">
            <p>${d.summary}</p>
            ${entityTags}
            <img src="https://dummyimage.com/300">
        </div>
        <footer class="card-footer">
            <a href="#" class="card-footer-item">Visualize</a>
            <a href="#" class="card-footer-item" style="color: #ff6384" onclick="deleteNode('${d.id}')">Delete</a>
        </footer>              
    `);

    $(".tooltip-close").click(function(event) { 
        // TODO: very hacky
        parentG = d3.select(event.target).node().parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode;
        selectedCircle = parentG.childNodes[0];
        selectedCircle.classList.remove('clicked');
        nodeGroup.select('.tooltip').remove();
        if (!topicMode)
            nodeGroup.lower();
        link.lower();
        // linkOverlay.lower();
        clickedNode = null; // Reset the clicked node
    })

    // Bring tooltip to the foreground
    nodeGroup.raise();

    let lastPositionX = 0;
    let lastPositionY = 0;
    let initialDragX, initialDragY;
    // Tooltip drag functions
    function dragStartedTooltip(event, d) {
        initialDragX = event.x - lastPositionX;
        initialDragY = event.y - lastPositionY;
        nodeGroup.raise();
    }

    function draggedTooltip(event, d) {
        const dx = event.x - initialDragX;
        const dy = event.y - initialDragY;
        tooltipGroup.attr('transform', `translate(${dx}, ${dy})`);
        lastPositionX = dx;
        lastPositionY = dy;
    }

    function dragEndedTooltip(event, d) {
        // Translate the tooltip to the final mouse position
    }

    // TODO: This has rendering errors when zoomed out far enough
    // Set element height dynamically
    // Get the current zoom level
    const currentZoomLevel = d3.zoomTransform(nodeGroup.node()).k;
    var divHeight = div.node().getBoundingClientRect().height;
    foreignObject.attr('height', (divHeight/currentZoomLevel) + 20);
    
}

function createSummaryTooltip(selectedCircle, summary, event) {
    const tooltipWidth = 300;
    const tooltipHeight = 400;

    // Remove existing tooltip for the clicked node
    // nodeSelection.filter(data => data.id === d.id).select('.tooltip').remove();

    // const nodeGroup = nodeSelection.filter(data => data.id === d.id);

    const nodeGroup = selectedCircle;

    // Create a new group for the tooltip
    const tooltipGroup = nodeGroup
        .append('g')
        .attr('class', 'tooltip')
        .call(d3.drag() // Add the drag behavior to the tooltip group
            .on('start', dragStartedTooltip)
            .on('drag', draggedTooltip)
            .on('end', dragEndedTooltip));

    // Create a foreignObject to hold the HTML content
    const foreignObject = tooltipGroup.append('foreignObject')
        .attr('x', 20) // Offset from the node circle
        .attr('y', -20) // Offset from the node circle
        .attr('width', tooltipWidth)
        .attr('height', tooltipHeight)
        .style('z-index', '1000');

    // Append an HTML div within the foreignObject
    const div = foreignObject.append('xhtml:div')
        .attr('class', 'card')
        .style('width', `${tooltipWidth}px`);
        // .style('height', '500px');

    div.html(`
        <header class="card-header tooltip-header">
            <p class="card-header-title">Cluster Summary</p>
            <button class="card-header-icon" aria-label="more options">
                <span class="icon">
                    <i class="fa-solid fa-close tooltip-close"></i>
                </span>
            </button>
        </header>
        <div class="card-content card-summary">
            <p>${summary}</p>
        </div>
    `);

    $(".tooltip-close").click(function(event) { 
        // TODO: very hacky
        // parentG = d3.select(event.target).node().parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode;
        // selectedCircle = parentG.childNodes[0];
        // selectedCircle.classList.remove('clicked');
        nodeGroup.select('.tooltip').remove();
        if (!topicMode)
            nodeGroup.lower();
        link.lower();
        // linkOverlay.lower();
        clickedNode = null; // Reset the clicked node
    })

    // Bring tooltip to the foreground
    nodeGroup.raise();

    let lastPositionX = 0;
    let lastPositionY = 0;
    let initialDragX, initialDragY;
    // Tooltip drag functions
    function dragStartedTooltip(event, d) {
        initialDragX = event.x - lastPositionX;
        initialDragY = event.y - lastPositionY;
        nodeGroup.raise();
    }

    function draggedTooltip(event, d) {
        const dx = event.x - initialDragX;
        const dy = event.y - initialDragY;
        tooltipGroup.attr('transform', `translate(${dx}, ${dy})`);
        lastPositionX = dx;
        lastPositionY = dy;
    }

    function dragEndedTooltip(event, d) {
        // Translate the tooltip to the final mouse position
    }

    // TODO: This has rendering errors when zoomed out far enough
    // Set element height dynamically
    // Get the current zoom level
    const currentZoomLevel = d3.zoomTransform(nodeGroup.node()).k;
    var divHeight = div.node().getBoundingClientRect().height;
    foreignObject.attr('height', (divHeight/currentZoomLevel) + 20);
    
}