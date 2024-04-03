# Graph Visualizer Demo

This demo hosts an early frontend demo of the Graph Visualizer, as part of a larger Brandeis CLMS Capstone Project. To run it, make sure you have Flask installed (it is the only requirement!). Then, run:

```
python app.py
```

It will host the server at [localhost:5000](localhost:5000), which you can access via a web browser.

## Specification

The app simulates 5 MMIF files that have been uploaded to the graph visualizer. Each file is rendered as a node in a force-directed graph, with the nodes representing connections between document contents.

Specifically, each file (when uploaded to the functional graph visualizer) is run through a transformer-based summarizer (BART, currently). Named entities are extracted from each summary, and links between nodes are formed and rendered based on these shared entities.[^1]

[^1] Side note: Why not just extract Named Entities from the documents themselves? This would be feasible but potentially impractical, since almost every file is bound to share some trivial Named Entity (e.g., a numerical value or the word "today"). However, that doesn't necessarily rule this out as an area of experimentation. 

## Interacting with the simulation

- Nodes can be dragged around, thanks to the D3 Javascript library. 
- To see shared entities between two nodes, you can hover over an edge.
- The right panel contains an information view with a pie chart of app types. Hover over or select slices to visually filter nodes based on the apps their MMIF files contain.
- Click on a node to view more information. This currently includes the summary and the named entities contained within the summary, though the full version would show more information. 

    A MMIF view also has buttons for visualizing or deleting (not currently implemented). The `Visualize` button would redirect to the individual visualization for a given file, while the `Delete` button would delete the node from the simulation. 