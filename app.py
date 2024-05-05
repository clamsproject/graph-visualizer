from flask import Flask, render_template, request
import os
import json
import ast
from mmif import Mmif
from collections import Counter

from modeling.summarize import summarize_file, summarize_from_text
from modeling.ner import get_entities
from modeling.cluster import cluster_nodes
from modeling.topic_model import get_topics, train_topic_model
from modeling.date import extract_date
from modeling.thumbnails import get_thumbnail

from db import insert_data, get_all_data, delete_data

# TODO: dynamically change node size based on filesize
# TODO: maybe automatically change document base? or at least make it easy to change

app = Flask(__name__, static_url_path='/static')

# Get the absolute path to the static folder
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/all-nodes')
def get_all_nodes():
    nodes = get_all_data("nodes")
    nodes = [(id, 
              label, 
              apps.split(","), 
              summary, 
              long_summary,
              transcript, 
              entities.split(","), 
              date, 
              temp, 
              hidden) for id, label, apps, summary, long_summary, transcript, entities, date, temp, hidden in nodes]
    nodes = [dict(zip(["id", "label", "apps", "summary", "long_summary", "transcript", "entities", "date", "temp", "hidden"], node)) for node in nodes]
    return nodes 

@app.route('/delete', methods=['POST'])
def delete():
    try:
        id = request.json['id']
        delete_data("nodes", id)
        return json.dumps({"success": True})
    except Exception as e:
        return json.dumps({"error": e})

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    
    try:
        file = request.files['file']
        filename = file.filename.replace(".mmif", "").replace(".json", "")
        mmif = Mmif(file.read())
        summary, long_summary, transcript = summarize_file(mmif)
        entities = get_entities(transcript)
        # Store entities as list in descending order of frequency
        c = Counter(entities)
        entities = [entity for entity, _ in c.most_common(500)]
        date = extract_date(filename, mmif)
        thumnail_path = get_thumbnail(mmif)
        apps = [str(view.metadata.app) for view in mmif.views]
        new_node = { 'id': filename, 
                     'label': filename, 
                     'apps': ",".join(apps), 
                     'summary': summary, 
                     "long_summary": long_summary,
                     "transcript": transcript,
                     'entities': ",".join(entities), 
                     'date': date,
                     'temp': False, 
                     'hidden': False }        
        insert_data("nodes", new_node)
        # Un-stringify list entries to pass back to the app
        new_node['apps'] = new_node['apps'].split(",")
        new_node['entities'] = new_node['entities'].split(",")
        return json.dumps(new_node)
    except Exception as e:
        return json.dumps({"error": e})
    
@app.route('/cluster', methods=['GET'])
def cluster():
    nodes = get_all_nodes()
    clusters = cluster_nodes(nodes, 4)
    return json.dumps(clusters)

@app.route('/topic_model', methods=['GET'])
def topic_model():
    nodes = get_all_nodes()
    docs = [node['transcript'] for node in nodes]
    topic_names, topic_distr = get_topics(docs)
    res = {}
    res["names"] = topic_names
    res["probs"] = {nodes[i]["id"]: topic_distr[i] for i in range(len(nodes))}
    return json.dumps(res)

@app.route('/add_topics', methods=['POST'])
def addTopics():
    try:
        topics = request.json['topics']
        train_topic_model(topics)
        return topic_model()
    except Exception as e:
        return json.dumps({"error": e})

@app.route('/summarize_all', methods=['GET'])
def summarize_all():
    nodes = get_all_nodes()
    summaries = [node["summary"] for node in nodes]
    summaries = "<NEXT ARTICLE>".join(summaries)
    return summarize_from_text(summaries)

@app.route('/summarize_clusters', methods=['POST'])
def summarize_clusters():
    print("Summarizing clusters...")
    nodes = request.json['nodes']
    n_clusters = max([node['cluster'] for node in nodes]) + 1
    cluster_texts = [" ".join([node['summary'] for node in nodes if node['cluster'] == i]) for i in range(n_clusters)]
    cluster_summaries = [summarize_from_text(cluster_text)[1] for cluster_text in cluster_texts]
    # nodes = get_all_nodes()
    # print(nodes)
    return cluster_summaries
    


if __name__ == '__main__':
    app.run(debug=True)