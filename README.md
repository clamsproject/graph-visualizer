# MMIF Graph Visualizer

This repository uses the Gemma3 model from Ollama to summarize transcripts in MMIF (https://mmif.clams.ai/) files. 


![screenshot](https://github.com/haydenmccormick/graph-visualizer/assets/74222796/a32f5379-e463-4af9-8dc9-d78206f79aa2)

## Quick Start

1. Prerequisites:
Before running the script, ensure you have the following installed:
a. Python 3.8+ (recommended to use a virtual environment)
b. Ollama – for running the gemma3 model locally
c. Torch – for text processing (if needed by any preprocessing logic)
d. MMIF-Python – for working with MMIF files

2. Installation
a. Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/clams-transcript-summarizer.git
cd clams-transcript-summarizer
pip install -r requirements.txt

b. Make sure the Ollama app is running, and the Gemma3 model is available:
```bash
ollama run gemma3

3. Usage:
Run the summarizer with an MMIF file that includes ASR transcript data:

```bash
python3 summarize.py /path/to/your/transcript_file.json





## Directory Structure

This project is heavily centered around client-side Javascript code, with Python used for backend modeling. The directory structure is as follows:

    - README.md
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
        - constants
           - styles.css
           - favicon.ico
        - scripts
           - cloud.js [Interactive word cloud]
           - cluster.js [K-means cluster visualization]
           - filter-panel.js [Side panel for filtering nodes]
           - graph.js [Base code for rendering the d3 force-directed graph]
           - search.js [Search/filter functionality across visualizations]
           - timeline.js [Interactive custom timeline of documents]
           - tooltip.js [Interactive tooltips when MMIF nodes are clicked]
           - topic-model.js [Like cluster.js, implements topic modeling visualizations]
    -modeling
        - cluster.py [K-means clustering implementation]
        - date.py [Date scraping]
        - get_descriptions.py [Description scraping from AAPB API]
        - ner.py [Spacy named entity extraction]
        - summarize.py [Abstractive summarization using Gemma3]
        - topic_model.py [Topic modelling using Gemma3]
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
