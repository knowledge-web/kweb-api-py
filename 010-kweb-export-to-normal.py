"""
How to Use This Script:

This script converts JSON files to SQLite databases and creates a new ZIP file with the SQLite data.

Usage:
    python script.py [input_zip_file] [output_zip_file]

Arguments:
    input_zip_file:  The path to the input ZIP file containing JSON files. (Optional; defaults to 'Brain-master.zip')
    output_zip_file: The path where the output ZIP file will be saved. (Optional; defaults to 'Brain.zip')

Environment Variables:
    KEEP_ALL_DATA: If set, the script will keep all JSON files. Otherwise, it will only keep 'thoughts.json' and 'links.json'.

Example:
    python script.py Input.zip Output.zip

Note:
    If the script encounters malformed JSON, it will skip that particular file.

"""

import zipfile
import os
import json
import sqlite3
import argparse
import shutil

def create_table_from_dict(cursor, table_name, sample_dict):
    columns = ', '.join([f"{key} TEXT" for key in sample_dict.keys()])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

def insert_dict_into_table(cursor, table_name, data_dict):
    keys = ', '.join(data_dict.keys())
    values = ', '.join(['?' for _ in data_dict.keys()])
    cursor.execute(f"INSERT INTO {table_name} ({keys}) VALUES ({values})", list(data_dict.values()))

def main(in_zip, out_zip):
    extract_dir = '/tmp/extracted_content/'
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir)

    with zipfile.ZipFile(in_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    root_folder = next(os.walk(extract_dir))[1][0]
    absolute_thoughts_json_path = os.path.join(extract_dir, root_folder, 'db/thoughts.json')

    if os.path.exists(absolute_thoughts_json_path):
        db_folder_path = os.path.join(extract_dir, root_folder, 'db')
        b02_folder_path = os.path.join(extract_dir, root_folder, 'B02')
        
        if not os.path.exists(b02_folder_path):
            os.makedirs(b02_folder_path)

        db_path = os.path.join(b02_folder_path, 'Brain.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        keep_all_data = os.environ.get('KEEP_ALL_DATA', False)

        for filename in os.listdir(db_folder_path):
            if filename.endswith('.json'):
                if not keep_all_data and filename not in ['thoughts.json', 'links.json']:
                    continue

                json_path = os.path.join(db_folder_path, filename)

                try:
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    continue

                table_name = filename.replace('.json', '')

                sample_data = data[0] if isinstance(data, list) else data
                if sample_data:
                    create_table_from_dict(cursor, table_name, sample_data)

                    if isinstance(data, list):
                        for item in data:
                            insert_dict_into_table(cursor, table_name, item)
                    elif isinstance(data, dict):
                        for value in data.values():
                            insert_dict_into_table(cursor, table_name, value)

        conn.commit()
        conn.close()

        with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            for root, dirs, files in os.walk(b02_folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, b02_folder_path)
                    new_zip.write(file_path, arcname)

    shutil.rmtree(extract_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert JSON files to SQLite and create a new ZIP.')
    parser.add_argument('in_zip', nargs='?', default='Brain-master.zip', help='Input ZIP file path')
    parser.add_argument('out_zip', nargs='?', default='Brain.zip', help='Output ZIP file path')
    
    args = parser.parse_args()
    main(args.in_zip, args.out_zip)