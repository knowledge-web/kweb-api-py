import zipfile
import os
import re
import sqlite3
from pathlib import Path
import sys

def main(zip_file_name, brain_db_path):
    # Extract the ZIP file
    extract_folder = '/tmp/Brain-pruned'
    Path(extract_folder).mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    # Connect to Brain.db (outside the ZIP)
    conn_brain = sqlite3.connect(brain_db_path)
    cursor_brain = conn_brain.cursor()

    # Fetch all IDs
    cursor_brain.execute("SELECT id FROM thoughts")
    thought_ids = [row[0] for row in cursor_brain.fetchall()]
    conn_brain.close()

    # Regex patterns
    name_patterns = {
        'name': re.compile(r'name\s*:\s*[\n]?([\w\s]+)', re.IGNORECASE),
        'alias': re.compile(r'alias\s*:\s*[\n]?([\w\s]+)', re.IGNORECASE),
        # Add other regex patterns here
    }

    # Extract data from markdown files
    extracted_data = []
    for thought_id in thought_ids:
        folder_path = os.path.join(extract_folder, thought_id)
        if os.path.isdir(folder_path):
            for md_file in os.listdir(folder_path):
                if md_file.endswith('.md'):
                    md_file_path = os.path.join(folder_path, md_file)
                    with open(md_file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        name, alias = "", ""

                        # Extract name
                        name_match = name_patterns['name'].search(content)
                        if name_match:
                            name = name_match.group(1).strip()

                        # Extract alias
                        alias_match = name_patterns['alias'].search(content)
                        if alias_match:
                            alias = alias_match.group(1).strip()

                        extracted_data.append((thought_id, name, alias))

    # Create kweb.db
    kweb_db_path = './kweb.db'
    conn_kweb = sqlite3.connect(kweb_db_path)
    cursor_kweb = conn_kweb.cursor()

    # Create metadata table
    cursor_kweb.execute('''
    CREATE TABLE IF NOT EXISTS metadata (
        id TEXT PRIMARY KEY,
        name TEXT,
        alias TEXT
    )
    ''')

    # Insert data
    cursor_kweb.executemany("INSERT OR REPLACE INTO metadata (id, name, alias) VALUES (?, ?, ?)", extracted_data)

    # Commit and close
    conn_kweb.commit()
    conn_kweb.close()

    # Print statistics
    conn_kweb = sqlite3.connect(kweb_db_path)
    cursor_kweb = conn_kweb.cursor()
    cursor_kweb.execute("SELECT COUNT(*) FROM metadata")
    total_rows = cursor_kweb.fetchone()[0]
    conn_kweb.close()

    print(f"Total rows in metadata: {total_rows}")

if __name__ == '__main__':
    zip_file_name = 'content.zip'  # Default ZIP file name
    brain_db_path = 'Brain.db'  # Default Brain.db path
    if len(sys.argv) > 2:
        zip_file_name = sys.argv[1]
        brain_db_path = sys.argv[2]
    main(zip_file_name, brain_db_path)
