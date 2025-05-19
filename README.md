# MMIF Graph Visualizer

This repository uses the Gemma3 model from Ollama to summarize transcripts in MMIF (https://mmif.clams.ai/) files. 


![screenshot](https://github.com/haydenmccormick/graph-visualizer/assets/74222796/a32f5379-e463-4af9-8dc9-d78206f79aa2)



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

# Running the models: 
1. Summarizer.py:
* Features:
- Support for two summarization methods:
1. Transformer-based summarization using BART 
2. LLM-based summarization using Gemma3 via Ollama (

* Automatic handling of long transcripts by chunking and hierarchical summarization
* Support for MMIF formatted files and raw transcript text files
* Configurable summary length

#Installation
Prerequisites:
1.Python 3
2. CUDA-compatible GPU recommended for transformer model (but will work on CPU)

#Setup

1. Clone this repository:
 git clone https://github.com/clamsproject/graph-visualizer
cd transcript-summarizer

2. Install the required dependencies

3.If using the LLM method, install and set up Ollama:
- Download and install Ollama 
- Start the Ollama service:
ollama serve
- Pull the Gemma3 model:
ollama pull gemma3


#Usage
The script can be run from the command line with the following arguments:
bashpython3 summarize.py [--llm | --transformer] input_file.json

Command-line Options
--llm: Use the LLM-based summarization method (requires Ollama with Gemma3)
--transformer: Use the transformer-based summarization method (using BART)
input_file: Path to the input file (MMIF JSON or raw transcript)


## Visualizations

Connections between nodes are rendered based on shared entities. Clicking a node will show its summary and top entity list, and clicking its summary text will toggle between full and truncated summaries. The nodes can be clustered via KMeans or Topic modeling. If clustering via KMeans, a long summary can be generated representing the content of the text in the clusters. If clustering via Topic Modeling, approximate distributions can be shown in relation to one another via a chart view. The filter panel also contains app type, word cloud, and timeline filters.

## A note on data

Because this application's domain is most likely restricted to news videos, its topic models were trained on ~2000 instances of NewsHour transcripts. Because the copyright on these items is dubious at best, I have not included them in the data directory. If you will only be using the pre-trained topic model, this isn't a problem, but if you want to **train** a topic model to fit your data, the BERTopic training script will throw an error (the only natural place in the app where this would come up is in adding custom zero-shot topics). Because BERTopic is an unsupervised algorithm, you can replace the NewsHour data with *any* custom data, as long the file is named `transcripts.csv` and the text you want to train the topic model on is under the column `transcript`.
