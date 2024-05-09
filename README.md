# MMIF Graph Visualizer

This repository hosts the code for the Graph Visualizer, a collection-level visualizer for [MMIF](https://mmif.clams.ai/) files which renders MMIF files as nodes in a D3 force-directed graph. For more information, read the project report in the `doc` directory.

## Quick Start

Currently, you can run the server in two ways:
1. Manually, with Python:
    * Install requirements: `pip install -r requirements.txt`
    * Unzip `data/topic_newshour.zip` in the `data` directory
    * Run `python app.py` to start the server. It will be accessible at `localhost:5555`
    * Run the mmif visualizer in parallel for access to visualization. **The MMIF visualizer should be exposed to port 5000**

2. Using Docker/Podman
* docker-compose up will spin up the Graph Visualizer and the MMIF visualizer, and connect them via a network.
* **WARNING**: Because the project contains a significant amount of modeling requirements and networking, building the container may take a while, and on my hardware has consistently crashed before completing. I have not been able to debug this -- running the files locally using your own distribution of Python is likely the most efficient and accessible way to start the service.

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


## Visualizations

Connections between nodes are rendered based on shared entities. Clicking a node will show its summary and top entity list, and clicking its summary text will toggle between full and truncated summaries. The nodes can be clustered via KMeans or Topic modeling. If clustering via KMeans, a long summary can be generated representing the content of the text in the clusters. If clustering via Topic Modeling, approximate distributions can be shown in relation to one another via a chart view. The filter panel also contains app type, word cloud, and timeline filters.

## A note on data

Because this application's domain is most likely restricted to news videos, its topic models were trained on ~2000 instances of NewsHour transcripts. Because the copyright on these items is dubious at best, I have not included them in the data directory. If you will only be using the pre-trained topic model, this isn't a problem, but if you want to **train** a topic model to fit your data, the BERTopic training script will throw an error (the only natural place in the app where this would come up is in adding custom zero-shot topics). Because BERTopic is an unsupervised algorithm, you can replace the NewsHour data with *any* custom data, as long the file is named `transcripts.csv` and the text you want to train the topic model on is under the column `transcript`.
