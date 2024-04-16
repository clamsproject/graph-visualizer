from flask import Flask, render_template, url_for
import os
import json
from flask import request
from modeling.summarize import summarize_file
from modeling.ner import get_entities
from db import insert_data, get_all_data, delete_data
import ast

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
    # TODO: HORRIBLE for security, make sure to fix
    nodes = [(id, label, ast.literal_eval(apps), summary, ast.literal_eval(entities), temp, hidden) for id, label, apps, summary, entities, temp, hidden in nodes]
    nodes = [dict(zip(["id", "label", "apps", "summary", "entities", "temp", "hidden"], node)) for node in nodes]
    return nodes

@app.route('/delete', methods=['POST'])
def delete():
    try:
        id = request.json['id']
        delete_data("nodes", id)
        return json.dumps({"success": True})
    except Exception as e:
        return json.dumps({"error": e})

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        filename = file.filename.replace(".mmif", "").replace(".json", "")
        summary = summarize_file(file.read())
        entities = get_entities(summary)
        new_node = { 'id': filename, 
                     'label': filename, 
                     'apps': "['doctr-wrapper']", 
                     'summary': summary, 
                     'entities': str(entities), 
                     'temp': False, 
                     'hidden': False }        
        insert_data("nodes", new_node)
        return json.dumps(new_node)
    except Exception as e:
        return json.dumps({"error": e})

if __name__ == '__main__':
    app.run(debug=True)