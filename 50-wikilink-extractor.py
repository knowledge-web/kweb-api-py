import os
import re
import sqlite3
import zipfile

# Define paths
db_folder_path = '.'
content_zip_path = './content.zip'

# Fetch thoughts from Brain.db
conn_brain = sqlite3.connect(os.path.join(db_folder_path, 'Brain.db'))
c_brain = conn_brain.cursor()
c_brain.execute('SELECT * FROM thoughts')
thoughts_data = c_brain.fetchall()
conn_brain.close()

# Regular expressions to find Markdown links
markdown_link_regex = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
name_wikipedia_link_regex = re.compile(r'name:.*?\[([^\]]+)\]\((https://en\.wikipedia\.org[^)]+)\)', re.IGNORECASE)

# Initialize a dictionary to map thought Ids to Wikipedia links or NULL
id_to_wikilink_map = {str(thought[0]): None for thought in thoughts_data}

# Loop through the .md files in content.zip to update the Wikipedia links or keep NULL
with zipfile.ZipFile(content_zip_path, 'r') as zip_ref:
    for file in zip_ref.namelist():
        if file.endswith('.md'):
            folder_name = os.path.basename(os.path.dirname(file))
            
            with zip_ref.open(file) as f:
                content = f.read().decode('utf-8')
                
            wikilink = None
            for link_text, link_url in markdown_link_regex.findall(content):
                if 'wikipedia.org' in link_url:
                    wikilink = link_url
                    break
            for link_text, link_url in name_wikipedia_link_regex.findall(content):
                wikilink = link_url
                break
            
            id_to_wikilink_map[folder_name] = wikilink

# Connect to kweb.db, create if not existing
conn_kweb = sqlite3.connect('kweb.db')
c_kweb = conn_kweb.cursor()
c_kweb.execute('''CREATE TABLE IF NOT EXISTS nodes (id TEXT PRIMARY KEY, wikilink TEXT)''')

# Check if the column 'wikilink' exists
c_kweb.execute("PRAGMA table_info(nodes)")
columns = [column[1] for column in c_kweb.fetchall()]

if 'wikilink' not in columns:
    c_kweb.execute("ALTER TABLE nodes ADD COLUMN wikilink TEXT")

# Insert/Update the mapped data into the table
for thought_id, wikilink in id_to_wikilink_map.items():
    c_kweb.execute("INSERT OR REPLACE INTO nodes (id, wikilink) VALUES (?, ?)", (thought_id, wikilink))

# Commit and close
conn_kweb.commit()
conn_kweb.close()
