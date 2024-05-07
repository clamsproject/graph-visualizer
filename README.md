# MMIF Graph Visualizer

This repository hosts the code for the Graph Visualizer, a collection-level visualizer for [MMIF](https://mmif.clams.ai/) files which renders MMIF files as nodes in a D3 force-directed graph. For more information, read the project report in the `doc` directory.

## Quick Start

Currently, you can run the server in two ways:
1. Manually, with Python:
    * Install requirements: `pip install -r requirements.txt`
    * Unzip `data/topic_newshour.zip` in the `data` directory
    * Run the mmif visualizer in parallel for access to visualization. **The MMIF visualizer should be exposed to port 5000**

2. Using Docker/Podman
* docker-compose up will spin up the Graph Visualizer and the MMIF visualizer, and connect them via a network.
* **WARNING**: Because the project contains a significant amount of networking, building the container may take a while, and will almost certainly crash before building the containers. I have not been able to debug this -- running the files locally using your own distribution of Python is likely the most efficient and accessible way to start the service.

## Directory Structure

This project is heavily centered around client-side Javascript code, with Python used for backend modeling. The directory structure is as follows:

    - README.md
    - doc                           
        - project_report.md
          [Main project report and specification]
    - data
        - topic_newshour.zip
          [The saved weights of the topic model trained on NewsHour transcripts]
    - app.py
      [The main Flask server code]
    - db.py
      [Implementation of an SQLite server for storing node information]
    - eval.py
      [Implementation of transformer question-generation for visualization eval]
    - static
          [implementations of different interactive page elements]
        - cloud.js [Interactive word cloud]
        - cluster.js [K-means cluster visualization]
        - filter-panel.js [Side panel for filtering nodes]
        - graph.js [Base code for rendering the d3 force-directed graph]
        - search.js [Search/filter functionality across visualizations]
        - timeline.js [Interactive custom timeline of documents]
        - tooltip.js [Interactive tooltips when MMIF nodes are clicked]
        - topic-model.js [Like cluster.js, implements topic modeling visualizations]
        - styles.css [self-explanatory]
    -modeling
        - cluster.py [K-means clustering implementation]
        - date.py [Date scraping]
        - get_descriptions.py [Description scraping from AAPB API]
        - ner.py [Spacy named entity extraction]
        - summarize.py [Abstractive summarization using BART]
        - topic_model.py [Topic modelling using BERTopic]
    - preprocessing/preprocess.py [functions for building description dataset]
    - templates
        - index.html
          [The root HTML page the visualization is built off of]
        - upload.html
          [A batch uploader accessible at localhost:5555/upload]
    - tmp
      [Directory for storing intermediate MMIF files before they are passed to the visualizer]