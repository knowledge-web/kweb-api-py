# Importing required libraries
import zipfile
import shutil
import os
import tempfile

# Define the function to perform the extraction and zipping tasks
def extract_and_zip(src_zip_path, dest_zip_name):
    # Create a temporary directory to extract files
    temp_dir = tempfile.mkdtemp()

    # Extract the zip file to the temporary directory
    with zipfile.ZipFile(src_zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Move the Brain.db file to the current directory
    brain_db_path = os.path.join(temp_dir, 'Brain.db')
    shutil.move(brain_db_path, './Brain.db')

    # Create a new zip file with remaining content (excluding Brain.db)
    with zipfile.ZipFile(dest_zip_name, 'w', zipfile.ZIP_DEFLATED) as new_zip:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                new_zip.write(file_path, arcname)

    # Cleanup: Remove the temporary directory
    shutil.rmtree(temp_dir)

# Example usage (you can replace these paths with your own)
extract_and_zip('Brain-pruned.zip', 'content.zip')
