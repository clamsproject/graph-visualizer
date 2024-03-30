from flask import Flask, render_template, url_for
import os

app = Flask(__name__, static_url_path='/static')

# Get the absolute path to the static folder
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index/')
def root():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)