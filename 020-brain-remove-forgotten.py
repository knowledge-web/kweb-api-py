
import zipfile
import os
import sqlite3
import shutil
import sys

# Command-line arguments
in_zip = sys.argv[1] if len(sys.argv) > 1 else 'Brain.zip'
out_zip = sys.argv[2] if len(sys.argv) > 2 else 'Brain-pruned.zip'

# Unzipping the uploaded file
zip_path = in_zip
extract_dir = '/tmp/extracted_folder/'

if not os.path.exists(extract_dir):
    os.makedirs(extract_dir)

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Connecting to SQLite database
brain_db_path = os.path.join(extract_dir, 'Brain.db')

if os.path.exists(brain_db_path):
    conn = sqlite3.connect(brain_db_path)
    cursor = conn.cursor()

    # Removing nodes with non-null ForgottenDateTime and logging the count
    cursor.execute(
        "SELECT COUNT(*) FROM thoughts WHERE ForgottenDateTime IS NOT NULL;")
    forgotten_count = cursor.fetchone()[0]
    cursor.execute("DELETE FROM thoughts WHERE ForgottenDateTime IS NOT NULL;")
    conn.commit()
    print(f"Removed {forgotten_count} entries with non-null ForgottenDateTime.")

    # Removing unused folders and logging the count
    cursor.execute("SELECT Id FROM thoughts;")
    remaining_ids = set(row[0] for row in cursor.fetchall())
    removed_folders_count = 0

    for folder_name in os.listdir(extract_dir):
        folder_path = os.path.join(extract_dir, folder_name)
        if folder_name not in remaining_ids and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
            removed_folders_count += 1

    print(f"Removed {removed_folders_count} unused folders.")

    # Modifying the link removal query to keep links with Kind=2
    cursor.execute(
        "SELECT COUNT(*) FROM links WHERE (thoughtIdA NOT IN (SELECT Id FROM thoughts) OR thoughtIdB NOT IN (SELECT Id FROM thoughts)) AND Kind != 2;"
    )
    invalid_links_count = cursor.fetchone()[0]
    cursor.execute(
        "DELETE FROM links WHERE (thoughtIdA NOT IN (SELECT Id FROM thoughts) OR thoughtIdB NOT IN (SELECT Id FROM thoughts)) AND Kind != 2;"
    )
    conn.commit()
    print(f"Removed {invalid_links_count} invalid links.")

    # Closing database connection
    conn.close()

    # Creating a new compressed zip file
    compressed_zip_path = out_zip
    with zipfile.ZipFile(compressed_zip_path, 'w',
                         zipfile.ZIP_DEFLATED) as new_zip:
        for root, _, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, extract_dir)
                new_zip.write(file_path, arcname)

    # Cleaning up temporary extracted folder
    shutil.rmtree(extract_dir)
else:
    print("Brain.db not found in the extracted folder.")
