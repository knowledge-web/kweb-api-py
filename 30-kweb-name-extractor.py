import zipfile
import os
import re
import sqlite3
from pathlib import Path
import sys

def main(zip_file_name):
    # Extract the ZIP file
    extract_folder = './Brain-pruned'
    Path(extract_folder).mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
        
    # Connect to Brain.db
    brain_db_path = os.path.join(extract_folder, 'Brain.db')
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
        'aka': re.compile(r'aka\s*:\s*[\n]?([\w\s]+)', re.IGNORECASE),
        'nickname': re.compile(r'nickname\s*:\s*[\n]?([\w\s]+)', re.IGNORECASE),
        'full_name': re.compile(r'full\s*name\s*:\s*[\n]?([\w\s]+)', re.IGNORECASE)
    }
    
    # Extract data
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
                        
                        full_name_match = name_patterns['full_name'].search(content)
                        name_match = name_patterns['name'].search(content)
                        if full_name_match:
                            name = full_name_match.group(1).strip()
                        elif name_match:
                            name = name_match.group(1).strip()
                        
                        alias_match = name_patterns['alias'].search(content)
                        nickname_match = name_patterns['nickname'].search(content)
                        aka_match = name_patterns['aka'].search(content)
                        if alias_match:
                            alias = alias_match.group(1).strip()
                        elif nickname_match:
                            alias = nickname_match.group(1).strip()
                        elif aka_match:
                            alias = aka_match.group(1).strip()
                        
                        extracted_data.append((thought_id, name, alias))
    
    # Create kweb.db
    kweb_db_path = './kweb.db'
    conn_kweb = sqlite3.connect(kweb_db_path)
    cursor_kweb = conn_kweb.cursor()
    cursor_kweb.execute('''
    CREATE TABLE IF NOT EXISTS thoughts_data (
        id TEXT PRIMARY KEY,
        name TEXT,
        alias TEXT
    )
    ''')
    
    # Insert all IDs with empty name and alias
    all_ids_data = [(thought_id, "", "") for thought_id in thought_ids]
    cursor_kweb.executemany("INSERT OR REPLACE INTO thoughts_data (id, name, alias) VALUES (?, ?, ?)", all_ids_data)
    
    # Update with extracted data
    cursor_kweb.executemany("INSERT OR REPLACE INTO thoughts_data (id, name, alias) VALUES (?, ?, ?)", extracted_data)
    
    # Commit and close
    conn_kweb.commit()
    conn_kweb.close()

# Re-connect to count the total number of rows in the updated kweb.db
    conn_kweb = sqlite3.connect(kweb_db_path)
    cursor_kweb = conn_kweb.cursor()
    cursor_kweb.execute("SELECT COUNT(*) FROM thoughts_data")
    total_rows_updated = cursor_kweb.fetchone()[0]
    cursor_kweb.execute("SELECT COUNT(*) FROM thoughts_data WHERE name != ''")
    total_names = cursor_kweb.fetchone()[0]
    cursor_kweb.execute("SELECT COUNT(*) FROM thoughts_data WHERE alias != ''")
    total_aliases = cursor_kweb.fetchone()[0]
    conn_kweb.close()

    print(f"Total rows: {total_rows_updated}")
    print(f"Total names: {total_names}")
    print(f"Total aliases: {total_aliases}")

if __name__ == '__main__':
    zip_file_name = 'Brain-pruned.zip'  # Default ZIP file name
    if len(sys.argv) > 1:
        zip_file_name = sys.argv[1]  # Update if provided as CLI argument
    main(zip_file_name)
