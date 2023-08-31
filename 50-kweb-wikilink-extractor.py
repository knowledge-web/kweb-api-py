import os
import re
import json
import sqlite3

# TODO modify this to add nodes.wikilink to kweb.db instead (if db not existing; create?)

# Define paths
db_folder_path = 'path/to/db'
b02_folder_path = 'path/to/B02'

# Load the thoughts data from filtered_thoughts.json
with open(os.path.join(db_folder_path, 'filtered_thoughts.json'), 'r') as f:
    thoughts_data = json.load(f)

# Regular expressions to find Markdown links
markdown_link_regex = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
name_wikipedia_link_regex = re.compile(r'name:.*?\[([^\]]+)\]\((https://en\.wikipedia\.org[^)]+)\)', re.IGNORECASE)

# Initialize a dictionary to map thought Ids to Wikipedia links or NULL
id_to_wikilink_map = {thought['Id']: None for thought in thoughts_data}

# Loop through the .md files in B02 to update the Wikipedia links or keep NULL
for root, dirs, files in os.walk(b02_folder_path):
    for file in files:
        if file.endswith('.md'):
            file_path = os.path.join(root, file)
            folder_name = os.path.basename(os.path.dirname(file_path))
            
            # Read the .md file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to find a Wikipedia link matching any of the patterns
            wikilink = None
            for link_text, link_url in markdown_link_regex.findall(content):
                if 'wikipedia.org' in link_url:
                    wikilink = link_url
                    break
            for link_text, link_url in name_wikipedia_link_regex.findall(content):
                wikilink = link_url
                break
            
            # Update the mapping with the found link or keep NULL
            id_to_wikilink_map[folder_name] = wikilink

# Create SQLite3 database and table
db_path = 'kweb.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS wikipedia_links (id TEXT PRIMARY KEY, wikilink TEXT)''')

# Insert the mapped data into the table
for thought_id, wikilink in id_to_wikilink_map.items():
    c.execute("INSERT INTO wikipedia_links (id, wikilink) VALUES (?, ?)", (thought_id, wikilink))

# Commit and close
conn.commit()
conn.close()
