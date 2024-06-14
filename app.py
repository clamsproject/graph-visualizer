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

from db import insert_data, get_all_data, delete_data
import requests
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')
# Enable CORS for all routes
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/all-nodes')
def get_all_nodes():
    nodes = get_all_data("nodes")
    nodes = [(id, 
              filename,
              label, 
              apps.split(","), 
              summary, 
              long_summary,
              transcript, 
              entities.split(","), 
              date, 
              temp, 
              hidden) for id, filename, label, apps, summary, long_summary, transcript, entities, date, temp, hidden in nodes]
    nodes = [dict(zip(["id", "filename", "label", "apps", "summary", "long_summary", "transcript", "entities", "date", "temp", "hidden"], node)) for node in nodes]
    return nodes 

@app.route('/delete', methods=['POST'])
def delete():
    try:
        id = request.json['id']
        nodes = get_all_nodes()
        node = [node for node in nodes if node['id'] == id][0]
        filename = node['filename']
        delete_data("nodes", id)

        # Delete the MMIF file from tmp
        tmp_filename = os.path.join('tmp', filename)
        os.remove(tmp_filename)

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
        file_content = file.read()
        mmif = Mmif(file_content)

        # Save the MMIF file to tmp
        tmp_filename = os.path.join('tmp', file.filename)
        with open(tmp_filename, 'wb') as tmp_file:
            tmp_file.write(file_content)
        
        summary, long_summary, transcript = summarize_file(mmif)
        entities = get_entities(transcript)

        # Store entities as list in descending order of frequency
        c = Counter(entities)
        entities = [entity.text for entity, _ in c.most_common(500)]
        date = extract_date(file.filename, mmif)
        apps = [str(view.metadata.app) for view in mmif.views]
        new_node = { 'id': filename, 
                     'filename': file.filename,
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
    
@app.route('/cluster', methods=['POST'])
def cluster():
    nodes = request.json['nodes']
    clusters = cluster_nodes(nodes, 4)
    return json.dumps(clusters)

@app.route('/topic_model', methods=['POST'])
def topic_model():
    nodes = request.json['nodes']
    docs = [node['long_summary'] for node in nodes]
    topic_names, topic_distr = get_topics(docs)
    res = {}
    res["names"] = topic_names
    res["probs"] = {nodes[i]["id"]: topic_distr[i] for i in range(len(nodes))}
    return json.dumps(res)

@app.route('/add_topics', methods=['GET'])
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
    return cluster_summaries

@app.route('/visualize', methods=['POST'])
def visualize():
    id = request.json['id']
    nodes = get_all_nodes()
    node = [node for node in nodes if node['id'] == id][0]
    filename = node['filename']
    
    # Redirect to the visualization page with the id
    file_path = os.path.join('tmp', filename)
    files = {'file': open(file_path, 'rb')}
    # The visualizer returns the document id if curl is in the headers
    headers = {'User-Agent': 'basically curl'}

    res = requests.post('http://localhost:5000/upload', files=files, headers=headers)
    return {"res": res.text}
    
    


if __name__ == '__main__':
    app.run(debug=False, port=5555)