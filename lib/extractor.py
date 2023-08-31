import os
import zipfile

def extract_unless_present(db_filename="Brain.db", zip_filename="Brain.zip"):
    # Check if the database file already exists
    if not os.path.exists(db_filename):
        # Extract the database file from the ZIP file
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall('.')
            print(f"{db_filename} extracted from {zip_filename}")
    else:
        print(f"{db_filename} already exists. No extraction needed.")
