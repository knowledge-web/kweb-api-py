
from flask import Flask, jsonify, send_from_directory, make_response
import os
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("kweb.db")
    return conn

@app.route('/nodes', methods=['GET'])
def get_nodes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM nodes')
    nodes = cursor.fetchall()
    conn.close()
    return jsonify([{'id': id, 'name': name} for id, name in nodes])

@app.route('/nodes/<int:node_id>', methods=['GET'])
def get_node(node_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM nodes WHERE id = ?', (node_id,))
    node = cursor.fetchone()
    if node is None:
        return jsonify({'error': 'Node not found'}), 404
    cursor.execute('SELECT * FROM links WHERE source = ? OR destination = ?', (node_id, node_id))
    links = cursor.fetchall()
    neighbor_ids = set()
    for source, destination in links:
        neighbor_ids.add(source if source != node_id else destination)
    nodes = [dict(zip([column[0] for column in cursor.description], row)) for row in [node]]
    for neighbor_id in neighbor_ids:
        cursor.execute('SELECT * FROM nodes WHERE id = ?', (neighbor_id,))
        nodes.append(dict(zip([column[0] for column in cursor.description], cursor.fetchone())))
    conn.close()
    return jsonify({'nodes': nodes, 'links': links})

@app.route('/f/<path:filename>', methods=['GET'])
def serve_files(filename):
    return send_from_directory('.', filename)

@app.route('/f/', methods=['GET'])
def list_files():
    files = os.listdir('.')
    file_links = [f'<li><a href="/f/{file}">{file}</a></li>' for file in files]
    return make_response(f'<html><body><ul>{" ".join(file_links)}</ul></body></html>', 200, {'Content-Type': 'text/html'})

@app.route('/', methods=['GET'])
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {}
    for table in ['nodes', 'links', 'metadata']:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        stats[table] = cursor.fetchone()[0]
    conn.close()
    doc_html = "<h1>API Documentation</h1>" +                "<ul>" +                "<li><a href='/nodes'>/nodes</a> - List all node names and ids.</li>" +                "<li>/nodes/:id - Fetch a node by its id along with its neighbors.</li>" +                "<li><a href='/f/'>/f/</a> - File listing.</li>" +                "<li>/f/:filename - Serve static files.</li>" +                "</ul>"
    return make_response(f'<html><body>' +                          f'<h1>Stats</h1>' +                          f'<p>Nodes: {stats["nodes"]}</p>' +                          f'<p>Links: {stats["links"]}</p>' +                          f'<p>Metadata: {stats["metadata"]}</p>' +                          f'{doc_html}' +                          f'</body></html>', 200, {'Content-Type': 'text/html'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)