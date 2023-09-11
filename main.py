from flask import Flask, jsonify, request, send_file, send_from_directory, make_response
from flask_cors import CORS
import sqlite3
import os
import zipfile
import re
import json

# FIXME Setting API_KEY header does not seem to work only query param ?API_KEY=... does

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Function to unzip media.zip to a temporary folder
def unzip_media_to_tmp():
    with zipfile.ZipFile('./media.zip', 'r') as zip_ref:
        zip_ref.extractall('/tmp/media')

# Unzip media.zip to /tmp/media on start
unzip_media_to_tmp()

# Function to unzip contents.zip to a temporary folder
def unzip_contents_to_tmp():
    with zipfile.ZipFile('content.zip', 'r') as zip_ref:
        zip_ref.extractall('/tmp/contents')

# Unzip contents.zip to /tmp/contents on start (if it makes sense to do so)
# Comment this line if you don't want to unzip on start
unzip_contents_to_tmp()

def query_db(query, args=(), one=False):
  with sqlite3.connect('./kweb.db') as con:
    cur = con.execute(query, args)
    rv = [
        dict((cur.description[idx][0], value) for idx, value in enumerate(row))
        for row in cur.fetchall()
    ]
  return (rv[0] if rv else None) if one else rv

@app.route("/nodes/", methods=['GET'])
def get_nodes():
  api_key = request.headers.get('API_KEY', None) or request.args.get('API_KEY', None)
  required_api_key = os.environ.get('API_KEY', None)

  nodes = query_db("SELECT id, name FROM nodes")

  if api_key != required_api_key:
    nodes = [node for node in nodes if not node['name'].startswith('Connections 4')]

  if all(node.get('name', None) == '' for node in nodes):
    return jsonify({"warning": "All node names are empty", "nodes": nodes})
  
  return jsonify(nodes)


@app.route("/nodes/<string:node_id>", methods=['GET'])
def get_node_with_neighbors(node_id):
    api_key = request.headers.get('API_KEY', None) or request.args.get('API_KEY', None)
    required_api_key = os.environ.get('API_KEY', None)
  
    nodes = query_db("SELECT * FROM nodes WHERE id=?", (node_id, ))
    links = query_db("SELECT * FROM links WHERE source=? OR target=?",
                     (node_id, node_id))
  
    # Initialize markdown content
    md_content = None

    # Check if Notes.md exists for this node_id
    md_file_path = f'/tmp/contents/{node_id}/Notes.md'
    if os.path.exists(md_file_path):
        with open(md_file_path, 'r') as md_file:
            md_content = md_file.read()

    # Add md content to the main node if it exists
    if nodes:
        nodes[0]['content'] = md_content
        nodes[0]['level'] = 0
    
    neighbor_ids = set()
    for link in links:
        neighbor_ids.add(link['source'])
        neighbor_ids.add(link['target'])
    neighbor_ids.discard(node_id)
    
    # Query for neighbor nodes
    neighbors = query_db(
        f"SELECT * FROM nodes WHERE id IN ({','.join(['?' for _ in neighbor_ids])})",
        tuple(neighbor_ids))

    if api_key != required_api_key:
        neighbors = [node for node in neighbors if not node['name'].startswith('Connections 4')]
  
    # Prepare birth and death as objects, and JSON decode places
    # FIXME Change DB, this confusing birth*, death* may still remain on the nodes
    for node in nodes + neighbors:
        node['birth'] = {}
        if 'birthdate' in node:
            node['birth']['date'] = node.pop('birthdate')
        if 'birthplace' in node:
            node['birth']['place'] = json.loads(node.pop('birthplace'))

        node['death'] = {}
        if 'deathdate' in node:
            node['death']['date'] = node.pop('deathdate')
        if 'deathplace' in node:
            node['death']['place'] = json.loads(node.pop('deathplace'))
      
        if 'places' in node:
            node['places'] = json.loads(node['places'])
    
        return jsonify({"nodes": nodes + neighbors, "links": links})

@app.route("/nodes/root", methods=['GET'])
def get_root_node():
  return get_node_with_neighbors("335994d7-2aff-564c-9c20-d2c362e82f8c")

@app.route("/files/<path:path>", methods=['GET'])
def get_file(path):
    if os.path.isdir(path):
        return file_list(path)
    else:
        directory, filename = os.path.split(path)
        return send_from_directory(directory, filename)

def file_list(directory='.'):
    files = os.listdir(directory)
    html_content = "<h1>File List</h1><ul>"
    for file in files:
        full_path = os.path.join(directory, file)
        if os.path.isdir(full_path):
            html_content += f"<li><a href='/files/{full_path}'>{file}/</a></li>"
        else:
            html_content += f"<li><a href='/files/{full_path}'>{file}</a></li>"
    html_content += "</ul>"
    return make_response(html_content, 200, {'Content-Type': 'text/html'})

@app.route("/icons/<string:node_id>", methods=['GET'])
def get_icon(node_id):
    # Validate node_id
    if not re.match(r'^[-0-9a-f]{36}$', node_id):
        return make_response("Invalid ID", 400)
    
    # Try to find the icon for the node
    icon_path = os.path.join('/tmp/media', node_id, '.data', 'Icon.png')
    if os.path.exists(icon_path):
        return send_file(icon_path)

    # If icon for the node doesn't exist, try to find the icon for its type
    node = query_db("SELECT * FROM nodes WHERE id=?", (node_id, ), one=True)
    if node and node.get('TypeId'):
        type_icon_path = os.path.join('/tmp/media', node['TypeId'], '.data', 'Icon.png')
        if os.path.exists(type_icon_path):
            return send_file(type_icon_path)

    return make_response("Not Found", 404)

@app.route("/f/", methods=['GET'])
def root_file_list():
    return file_list()

@app.route("/", methods=['GET'])
def index():
  try:
    table_names = query_db("SELECT name FROM sqlite_master WHERE type='table';")
    table_counts = {}
    missing_tables = []
    nodes_stats = {}
    links_stats = {}
    
    for table in ["nodes", "links", "metadata"]:
      if table not in [t["name"] for t in table_names]:
        missing_tables.append(table)
        
    for table in table_names:
      count = query_db(f"SELECT COUNT(*) as count FROM {table['name']}", one=True)
      table_counts[table['name']] = count['count']
      
      # If it's the 'nodes' table, get additional stats
      if table['name'] == 'nodes':
        column_names = query_db("PRAGMA table_info(nodes);")
        columns = [col['name'] for col in column_names]

        if 'wikilink' in columns:
          wikilink_count = query_db("SELECT COUNT(*) as count FROM nodes WHERE wikilink IS NOT NULL", one=True)
          nodes_stats['wikilink_count'] = wikilink_count['count']

        if 'wikidataId' in columns:
          wikidataId_count = query_db("SELECT COUNT(*) as count FROM nodes WHERE wikidataId IS NOT NULL", one=True)
          nodes_stats['wikidataId_count'] = wikidataId_count['count']

      # If it's the 'links' table, get additional stats
      if table['name'] == 'links':
        column_names = query_db("PRAGMA table_info(links);")
        columns = [col['name'] for col in column_names]

        if 'name' in columns:
          name_count = query_db("SELECT COUNT(*) as count FROM links WHERE name IS NOT NULL AND name != ''", one=True)
          links_stats['name_count'] = name_count['count']

    html_content = f"""
        <h1>Welcome to KWeb API</h1>
        <p><strong>Stats:</strong> {table_counts}</p>
        <p><strong>Nodes Stats:</strong> {nodes_stats}</p>
        <p><strong>Links Stats:</strong> {links_stats}</p>
        <p><strong>Missing Tables:</strong> {missing_tables}</p>
        <h2>API Endpoints:</h2>
        <ul>
            <li><a href='/nodes'>/nodes</a> - List all node names and IDs</li>
            <li><a href='/nodes/root'>/nodes/root</a> - Get the root node along with its neighbors</li>
        </ul>
        """

    return make_response(html_content, 200, {'Content-Type': 'text/html'})
  except Exception as e:
    return jsonify({"error": str(e)})

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000)
