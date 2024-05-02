let hoveredEntity = null;

function renderCloud() {
  d3.select("#wordCloud").selectAll("*").remove();
  [wordCounts, maxCount] = getAllDocWords();
  var layout = d3.layout.cloud()
    .size([430, 300])
    .words(Object.keys(wordCounts).map(function(d) {
      return { text: d, size: Math.sqrt(wordCounts[d] / maxCount) * 80, color: randomColor() };
    }))
    .padding(10)
    // .rotate(function() { return ~~(Math.random() * 2) * 90; })
    .rotate(0)
    .font("monospace")
    .fontSize(function(d) { return d.size; })
    .on("end", draw);

  layout.start();

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
}

// Call the cloud layout function when the DOM is ready
nodesPromise.then(renderCloud);

function getAllDocWords() {
  counts = {}
  max = 0;
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].hidden) continue;
    nodes[i].entities.forEach(entity => {
      if (entity in counts) counts[entity] += 1;
      else counts[entity] = 1;
      max = Math.max(max, counts[entity]);
    });
  }
  return [counts, max];
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
  searchFilter({value: entity, field: "all"}, section=`cloud_${entity}`);
}

function removeEntitySearch(entity) {
  removeSearchSection(`cloud_${entity}`);
}