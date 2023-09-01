from flask import Flask, jsonify, request, send_file, send_from_directory, make_response
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def query_db(query, args=(), one=False):
  with sqlite3.connect('./kweb.db') as con:
    cur = con.execute(query, args)
    rv = [
        dict((cur.description[idx][0], value) for idx, value in enumerate(row))
        for row in cur.fetchall()
    ]
  return (rv[0] if rv else None) if one else rv


@app.route("/nodes", methods=['GET'])
def get_nodes():
  nodes = query_db("SELECT id, name FROM nodes")
  if all(node.get('name', None) == '' for node in nodes):
    return jsonify({"warning": "All node names are empty", "nodes": nodes})
  return jsonify(nodes)


@app.route("/nodes/<string:node_id>", methods=['GET'])
def get_node_with_neighbors(node_id):
  nodes = query_db("SELECT * FROM nodes WHERE id=?", (node_id, ))
  links = query_db("SELECT * FROM links WHERE source=? OR target=?",
                   (node_id, node_id))
  neighbor_ids = set()
  for link in links:
    neighbor_ids.add(link['source'])
    neighbor_ids.add(link['target'])
  neighbor_ids.discard(node_id)
  neighbors = query_db(
      f"SELECT * FROM nodes WHERE id IN ({','.join(['?' for _ in neighbor_ids])})",
      tuple(neighbor_ids))
  return jsonify({"nodes": nodes + neighbors, "links": links})


@app.route("/nodes/root", methods=['GET'])
def get_root_node():
  return get_node_with_neighbors("335994d7-2aff-564c-9c20-d2c362e82f8c")


@app.route("/files/<path:path>", methods=['GET'])
def get_file(path):
  return send_from_directory('.', path)


@app.route("/f/", methods=['GET'])
def file_list():
  files = os.listdir('.')
  html_content = "<h1>File List</h1><ul>"
  for file in files:
    html_content += f"<li><a href='/files/{file}'>{file}</a></li>"
  html_content += "</ul>"
  return make_response(html_content, 200, {'Content-Type': 'text/html'})


@app.route("/", methods=['GET'])
def index():
  try:
    table_names = query_db(
        "SELECT name FROM sqlite_master WHERE type='table';")
    table_counts = {}
    missing_tables = []
    for table in ["nodes", "links", "metadata"]:
      if table not in [t["name"] for t in table_names]:
        missing_tables.append(table)
    for table in table_names:
      count = query_db(f"SELECT COUNT(*) as count FROM {table['name']}",
                       one=True)
      table_counts[table['name']] = count['count']

    html_content = f"""
        <h1>Welcome to KWeb API</h1>
        <p><strong>Stats:</strong> {table_counts}</p>
        <p><strong>Missing Tables:</strong> {missing_tables}</p>
        <h2>API Endpoints:</h2>
        <ul>
            <li><a href='/nodes'>/nodes</a> - List all node names and IDs</li>
            <li><a href='/nodes/root'>/nodes/root</a> - Get the root node along with its neighbors</li>
            <li><a href='/f/'>/f/</a> - List all files</li>
        </ul>
        """

    return make_response(html_content, 200, {'Content-Type': 'text/html'})
  except Exception as e:
    return jsonify({"error": str(e)})


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000)
