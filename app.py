from flask import Flask, render_template, url_for
import os
import json
from flask import request
from modeling.summarize import summarize_file
from modeling.ner import get_entities

# TODO: dynamically change node size based on filesize
# TODO: maybe automatically change document base? or at least make it easy to change

app = Flask(__name__, static_url_path='/static')

# Get the absolute path to the static folder
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        filename = file.filename
        summary = summarize_file(file.read())
        entities = get_entities(summary)
        new_node = { 'id': filename, 'label': filename, 'apps': ['doctr-wrapper'], 'summary': summary, 'entities': entities, 'temp': False }
        return json.dumps(new_node)
    except Exception as e:
        return json.dumps({"error": e})

if __name__ == '__main__':
    app.run(debug=True)