import zipfile
import os
import sqlite3
import shutil

# Unzip Brain.db
zip_file_path = '/path/to/Brain-pruned (1).zip'
extract_path = '/path/to/extracted/'
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Paths to the Brain.db and new kweb.db
brain_db_path = '/path/to/Brain.db'
kweb_db_path = '/path/to/kweb.db'

# Remove kweb.db if it already exists
if os.path.exists(kweb_db_path):
    os.remove(kweb_db_path)

# Connect to Brain.db
conn_brain = sqlite3.connect(brain_db_path)
cursor_brain = conn_brain.cursor()

# Fetch data from thoughts and links tables
cursor_brain.execute('SELECT Id, Name, Label, TypeId FROM thoughts')
thoughts_data = cursor_brain.fetchall()
cursor_brain.execute('SELECT Name, ThoughtIdA, ThoughtIdB FROM links')
links_data = cursor_brain.fetchall()

# Close connection to Brain.db
conn_brain.close()

# Create and connect to kweb.db
conn_kweb = sqlite3.connect(kweb_db_path)
cursor_kweb = conn_kweb.cursor()

# Create new tables
cursor_kweb.execute('''
    CREATE TABLE nodes (
        id TEXT PRIMARY KEY,
        name TEXT,
        label TEXT,
        typeId TEXT
    )
''')
cursor_kweb.execute('''
    CREATE TABLE links (
        name TEXT,
        source TEXT,
        target TEXT
    )
''')

# Insert data
cursor_kweb.executemany('INSERT INTO nodes (id, name, label, typeId) VALUES (?, ?, ?, ?)', thoughts_data)
cursor_kweb.executemany('INSERT INTO links (name, source, target) VALUES (?, ?, ?)', links_data)

# Commit and close connection
conn_kweb.commit()
conn_kweb.close()

# Move the kweb.db to a user-accessible location
download_path = '/path/to/download/kweb.db'
shutil.move(kweb_db_path, download_path)
