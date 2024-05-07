// function resetZoom() {
//     const desiredZoomLevel = 0.5;
//     const currentTransform = d3.zoomTransform(svg.node());
//     console.log('Current transform:', currentTransform);
//     svg.transition().duration(750).call(zoomBehavior.transform, d3.zoomIdentity.scale(desiredZoomLevel).translate(width/2,height/2));
//     const newTransform = d3.zoomTransform(svg.node());
//     console.log('New transform:', newTransform);

//     zoomBehavior.translateBy(svg.transition().duration(750), 0, 0);
//     zoomBehavior.scaleBy(svg.transition().duration(750), desiredZoomLevel);  
//   }
  
$(".topicModelButton").click(function () {
    if ($(this).hasClass("untopicmodeled")) {
        topicModel();
        $(this).removeClass("untopicmodeled");
        $(this).addClass("topicmodeled");
        $(this).text("Remove Topic Modeling");
    } else {
        unTopicModel();
        $(this).removeClass("topicmodeled");
        $(this).addClass("untopicmodeled");
        $(this).text("Topic Model");
    }
});

function topicModel() {
    $(".topicModelButton").addClass("is-loading");
    $(".clusterButton").addClass("is-static");
    fetch("/topic_model", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({nodes: nodes})
    
    })
        .then(response => response.json())
        .then(data => {
            $(".topicModelButton").removeClass("is-loading");
            setTopicData(data);
        })
}

function setTopicData(data) {
    uncluster();
    clusters = []
            probs = data["probs"];
            for (const [key, value] of Object.entries(probs)) {
                matchingNode = nodes.find(node => node.id == key);
                nodeProbs = value;
                topicNum = argMax(nodeProbs);
                if (!clusters.includes(topicNum)) {
                    matchingNode.cluster = clusters.length;
                    clusters.push(topicNum);
                }
                else {
                    matchingNode.cluster = clusters.indexOf(topicNum);
                }
            }

            topics = data;

            numClusters = clusters.length;
            clusterColors = getRandomColors(numClusters);
            updateGraph();

            $("#topicChartButton").removeClass("inactive");
            $("#clusterColorBox").removeAttr("disabled");
}

function unTopicModel() {
    $("#clusterColorBox").attr("disabled", true);
    $("#topicChartButton").addClass("inactive");
    $(".clusterButton").removeClass("is-static");
    if (!$("#returnButton").hasClass("inactive")) {
        $("#returnButton").addClass("inactive");
    }
    if ($("#sliderWithValue").attr("disabled")) {
        $("#sliderWithValue").removeAttr("disabled");
    }
    topics = null;
    uncluster();
}

function showTopicChart() {
    showTopicModel(topics);
    $(this).addClass("inactive");
}


function showTopicModel(data) {
    // $("#filterHeader").click();
    $("#sliderWithValue").attr("disabled", "disabled");
    $("#returnButton").removeClass("inactive");

    // resetZoom();

    
    frozen = true;
    
    let xTopicID = 0
    let yTopicID = 1

    const bottomButtonGroup = svg.append('foreignObject')
        .attr('class', 'bottom-button-group')
        .attr('transform', `translate(${width / 2}, ${height+50})`)
        .attr('width', 400)
        .attr('height', 2000)
        .html(`
            <div class="dropdown">
            <div class="dropdown-trigger">
            <button class="button" aria-haspopup="true" aria-controls="dropdown-menu">
                <span id="bottom-button-text">${data["names"][0]}</span>
                <span class="icon is-small">
                <i class="fas fa-angle-down" aria-hidden="true"></i>
                </span>
            </button>
            </div>
            <div class="dropdown-menu" id="dropdown-menu-bottom" role="menu">
            <div class="dropdown-content">
                <a href="#" class="add-topics dropdown-item">+ Add topic(s)</a>
                ${Object.values(data["names"]).map(topic => `<a href="#" class="dropdown-item topic-name">${topic}</a>`).join('')}
            </div>
            </div>
        </div>
            `);



    const leftButtonGroup = svg.append('foreignObject')
        .attr('class', 'left-button-group')
        .attr('transform', `translate(-375, ${height / 2})`)
        .attr('width', 370)
        .attr('height', 2000)
        .html(`
        <div class="dropdown">
            <div class="dropdown-trigger">
            <button class="button" aria-haspopup="true" aria-controls="dropdown-menu">
                <span id="left-button-text">${data["names"][1]}</span>
                <span class="icon is-small">
                <i class="fas fa-angle-down" aria-hidden="true"></i>
                </span>
            </button>
            </div>
            <div class="dropdown-menu" id="dropdown-menu-left" role="menu">
            <div class="dropdown-content">
                <a href="#" class="add-topics">+ Add topic(s)</a>
                ${Object.values(data["names"]).map(topic => `<a href="#" class="dropdown-item topic-name">${topic}</a>`).join('')}
            </div>
            </div>
        </div>
        `);        

    const bottomButton = bottomButtonGroup.append('rect')
        .attr('width', 100)
        .attr('height', 30)
        .attr('rx', 5)
        .attr('ry', 5)
        .attr('fill', 'steelblue')
        .on('click', handleBottomButtonClick);

    const leftButton = leftButtonGroup.append('rect')
        .attr('width', 100)
        .attr('height', 30)
        .attr('rx', 5)
        .attr('ry', 5)
        .attr('fill', 'steelblue')
        .attr('transform', 'rotate(-90)')
        .on('click', handleLeftButtonClick);

    bottomButtonGroup.append('text')
        .attr('x', 50)
        .attr('y', 20)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .text(data["names"][0]);

    leftButtonGroup.append('text')
        .attr('x', 20)
        .attr('y', 0)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .text(data["names"][1]);

    // Add a horizontal line above the bottom button group
    svg.append("line")
        .attr("x1", 0)
        .attr("y1", height)
        .attr("x2", width)
        .attr("y2", height)
        .attr("stroke", "black")
        .lower();

    // Add a vertical line to the right of the left button group
    svg.append("line")
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", 0)
        .attr("y2", height)
        .attr("stroke", "black")
        .lower();

        const pattern = svg.append('defs')
        .append('pattern')
        .attr('id', 'diagonalHatch')
        .attr('patternUnits', 'userSpaceOnUse')
        .attr('width', 100)
        .attr('height', 100)
        .append('image')
        .attr('xlink:href', `data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E`)
        .attr('opacity', 0.5)
        .attr('width', 100)
        .attr('height', 100)
        .lower();     
      
    topicBackground = svg.append('rect')
        .attr('class', 'topicBackground')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'url(#diagonalHatch)')
        .attr('x', 0)
        .attr('y', 0)
        .lower();
      
    simulation.stop();
    $(".link").remove();
    $(".topicLabel").remove();
    
    node
        .transition(d3.transition().duration(1000))
        .attr('transform', d => `translate(${data["probs"][d.id][0] * width}, ${height - (data["probs"][d.id][1] * height)})`);

    // svg.transition()
    //     .duration(750)
    //     .call(d3.zoom().on("zoom", zoomed), d3.zoomIdentity);


    $('.dropdown-trigger').click(function() {
        $(this).closest('.dropdown').toggleClass('is-active');
    });
    
    function getKeyByValue(object, value) {
        return Object.keys(object).find(key => object[key] === value);
      }

    // Add event listeners for dropdown items
    $('#dropdown-menu-bottom .topic-name').click(function() {
        const selectedTopic = $(this).text();
        $('#bottom-button-text').text(selectedTopic);
        $('.bottom-button-group .dropdown').removeClass('is-active');
        const topicID = getKeyByValue(data["names"], selectedTopic);
        xTopicID = topicID;
        node
        .transition(d3.transition().duration(1000))
        .attr('transform', d => `translate(${data["probs"][d.id][xTopicID] * width}, ${height - (data["probs"][d.id][yTopicID] * height)})`);
    });

    $('#dropdown-menu-left .topic-name').click(function() {
        const selectedTopic = $(this).text();
        $('#left-button-text').text(selectedTopic);
        $('.left-button-group .dropdown').removeClass('is-active');
        const topicID = getKeyByValue(data["names"], selectedTopic);
        yTopicID = topicID;
        node
        .transition(d3.transition().duration(1000))
        .attr('transform', d => `translate(${data["probs"][d.id][xTopicID] * width}, ${height - (data["probs"][d.id][yTopicID] * height)})`);
    });

    $(".add-topics").click(function() {
        showTopicMenu();
    });

    $(".modal-background, .modal-close").click(function() {
        hideTopicMenu();
    });

    function handleBottomButtonClick() {
        console.log('Bottom button clicked');
        // Add your logic here
    }

    function handleLeftButtonClick() {
        console.log('Left button clicked');
        // Add your logic here
    }

    topicMode = true;
}

function endTopicMode() {
    $("#returnButton").addClass("inactive");
    updateGraph();
    // showTopicChart();
    $("#sliderWithValue").removeAttr("disabled");
    topicMode = false;
}

let initialTopics = [];
let topicList = [];
function showTopicMenu() {
    $("#add-topic").addClass("is-active");
    console.log(topics);
    for (topicName of Object.values(topics["names"])) {
        // Filter out automatic topic names (TODO: hacky)
        if (topicName.includes("_")) {
            continue;
        }
        const tag = document.createElement('span');
        tag.textContent = topicName;
        tag.classList.add('tag', 'is-primary');
        $("#tagContainer").append(tag);

        initialTopics.push(topicName);
        topicList.push(topicName);
    }
}

function hideTopicMenu() {
    $("#add-topic").removeClass("is-active");
    if ($('.bottom-button-group .dropdown').hasClass("is-active")) {
        $('.bottom-button-group .dropdown').removeClass("is-active")
    }
    if ($('.left-button-group .dropdown').hasClass("is-active")) {
        $('.left-button-group .dropdown').removeClass("is-active")
    }
}

$("#topicInput").on("keypress", function(e) {
    if(e.which != 13) {
        return;
    }    
    const topicName = $(this).val();
    if (topicName) {
        const tag = document.createElement('span');
        tag.textContent = topicName;
        tag.classList.add('tag', 'is-primary');
        $("#tagContainer").append(tag);
        topicList.push(topicName);
        topicInput.value = '';            
    }
});

$("#cancelTopics").click(function(){
    topicList = [];
    hideTopicMenu();
})

$("#submitTopics").click(function(){
    if (topicList.length == 0 || initialTopics.toString() === topicList.toString()) {
        if ($("#topicInput").val() != '') {
            topicList.push($("#topicInput").val())
        }
        else
            return;
    }
    hideTopicMenu();
    showProgressBar();
    fetch('/add_topics', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({topics: topicList})
    })
    .then(response => response.json())
    .then(data => {
        hideProgressBar();
        setTopicData(data);
    });
})