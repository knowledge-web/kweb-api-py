from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Root endpoint that returns a simple "Hello 👋" message
@app.route('/')
def hello():
    return "Hello 👋"

# Endpoint to list all files in the current directory
@app.route('/f')
def list_files():
    files = os.listdir('.')
    file_list = "<ul>"
    for f in files:
        file_list += f'<li><a href="/f/{f}">{f}</a></li>'
    file_list += "</ul>"
    return file_list

# Endpoint to serve individual files
@app.route('/f/<path:filename>')
def serve_file(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  