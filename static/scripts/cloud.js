let hoveredEntity = null;

function renderCloud() {
  console.log("Rendering cloud...")
  d3.select("#wordCloud").selectAll("*").remove();
  [wordCounts, maxCount] = getAllDocWords();
  var layout = d3.layout.cloud()
    .size([430, 300])
    .words(Object.keys(wordCounts).map(function(d) {
      return { text: d, size: Math.sqrt(wordCounts[d] / maxCount) * 70 - 20, color: randomColor() };
    }))
    .padding(5)
    .rotate(0)
    .font("monospace")
    .fontSize(function(d) { return d.size; })
    .on("end", draw);

  function draw(words) {
    d3.select("#wordCloud").append("svg")
      .attr("width", layout.size()[0])
      .attr("height", layout.size()[1])
      .append("g")
      .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
      .selectAll("text")
      .data(words)
      .enter().append("text")
      .style("font-size", function(d) { return d.size + "px"; })
      .style("font-family", "monospace")
      .style("fill", function(d) { return d.color; })
      .attr("text-anchor", "middle")
      .attr("transform", function(d) {
        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
      })
      .on("mouseover", handleMouseOver)
      .on("mouseout", handleMouseOut)
      .on("click", handleClick)

      .text(function(d) { return d.text; });
  }

  // console.log("Done rendering cloud.")

layout.start();
}

// Call the cloud layout function when the DOM is ready
nodesPromise.then(renderCloud);

function getAllDocWords() {
  const wordSet = new Set();
  let max = 0;

  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].hidden) continue;

    for (const entity of nodes[i].entities) {
      wordSet.add(entity);
    }
  }

  const counts = {};
  for (const word of wordSet) {
    counts[word] = 0;
  }

  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].hidden) continue;

    for (const entity of nodes[i].entities) {
      counts[entity]++;
      max = Math.max(max, counts[entity]);
    }
  }

  const top50 = Object.keys(counts)
    .sort((a, b) => counts[b] - counts[a])
    .slice(0, 50)
    .reduce((obj, key) => {
      obj[key] = counts[key];
      return obj;
    }, {});

  // console.log(top50);

  return [top50, max];
}

function handleMouseOver(d, i) {
  d3.select(this).transition()
    .duration('50')
    .attr('opacity', '.5');
  d3.select(this)
    .classed('cloudHover', true)

  hoveredEntity = d.target.textContent;
  tick();

    // .on('click', searchEntity);
}

function handleMouseOut(d, i) {
  d3.select(this).transition()
    .duration('50')
    .attr('opacity', '1');
  d3.select(this)
    .classed('cloudHover', false);
  
  hoveredEntity = null;
  tick();
}

function handleClick(d, i) {
  if (d3.select(this).classed('cloudSelected')) {
    d3.select(this).classed('cloudSelected', false);
    removeEntitySearch(d.target.textContent);
    return;
  }
  d3.select(this).classed('cloudSelected', true);
  searchEntity(d.target.textContent);
}

function searchEntity(entity) {
  searchFilter({value: entity, field: "entity"}, section=`cloud_${entity}`);
}

function removeEntitySearch(entity) {
  removeSearchSection(`cloud_${entity}`);
}