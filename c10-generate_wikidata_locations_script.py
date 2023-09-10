
# Importing required libraries
import zipfile
import os
import json
import shutil

# Define paths
zip_file_path = './wikidata-cache.zip'
temp_extract_dir = '/tmp/wikidata-cache-extracted/'
output_json_path = './wikidata-locations.json'

# Function to extract all location IDs related to birthplace, death place, and places lived
def extract_relevant_location_ids(files, directory):
    location_ids = set()
    for file in files:
        file_path = os.path.join(directory, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Navigating to the 'claims' section if present
            entity_key = list(data.get('entities', {}).keys())[0]
            claims = data.get('entities', {}).get(entity_key, {}).get('claims', {})
            # Checking for properties related to locations (birthplace: P19, death place: P20, places lived: P551)
            for prop in ['P19', 'P20', 'P551']:
                if prop in claims:
                    for claim in claims[prop]:
                        if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                            location_id = claim['mainsnak']['datavalue']['value']['id']
                            location_ids.add(location_id)
        except Exception as e:
            continue
    return location_ids

# Create temp directory and extract zip file
os.makedirs(temp_extract_dir, exist_ok=True)
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(temp_extract_dir)

# List the files in the extracted directory
extracted_files_temp = os.listdir(temp_extract_dir)

# Extract all relevant location IDs
relevant_location_ids_temp = extract_relevant_location_ids(extracted_files_temp, temp_extract_dir)

# Initialize a dictionary with location IDs as keys and None as values
location_id_dict = {location_id: None for location_id in relevant_location_ids_temp}

# Save the dictionary to a JSON file
with open(output_json_path, 'w') as f:
    json.dump(location_id_dict, f)

# Cleanup: Remove the temporary directory
shutil.rmtree(temp_extract_dir)
