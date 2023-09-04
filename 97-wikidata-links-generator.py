
import os
import json
from zipfile import ZipFile
from collections import Counter

# Known P-values and their human-readable forms
known_p_values = {
    'P31': 'Instance of',
    'P1889': 'Different from',
    'P282': 'Writing system',
    'P407': 'Language of work or name',
    'P910': "Topic's main Wikimedia portal",
    'P279': 'Subclass of',
    'P5008': 'Wikishootme ID',
    'P2283': 'Uses',
    'P527': 'Has part'
}

# Function to filter claims and create a JSON object
def filter_and_store_claims(claims_dict):
    filtered_claims_json = {}
    for property_id, claim_list in claims_dict.items():
        claim_value = claim_list[0]['mainsnak'].get('datavalue', {}).get('value', None)
        if isinstance(claim_value, dict) and 'id' in claim_value:
            key = f"{property_id}-{claim_value['id']}"
            filtered_claims_json[key] = claim_value['id']
    return filtered_claims_json

# Initialize an empty JSON object to store all filtered claims
all_filtered_claims = {}

# Extract Wikidata cache
with ZipFile('./wikidata-cache.zip', 'r') as zip_ref:
    zip_ref.extractall('./wikidata-cache')

# Loop through the files in the cache
for file_name in os.listdir('./wikidata-cache'):
    if file_name.endswith('.json'):
        # Read the JSON file
        with open(os.path.join('./wikidata-cache', file_name), 'r') as f:
            wikidata_json = json.load(f)
        
        # Extract the claims
        claims_dict = wikidata_json.get('entities', {}).get(file_name.replace('.json', ''), {}).get('claims', {})
        
        # Filter and store the claims
        filtered_claims = filter_and_store_claims(claims_dict)
        if filtered_claims:
            all_filtered_claims[file_name.replace('.json', '')] = filtered_claims

# Reformat and make the claims human-readable
reformatted_claims = {}
for entity, claims in all_filtered_claims.items():
    for claim_key, claim_value in claims.items():
        new_key = f"{entity}-{claim_value}"
        reformatted_claims[new_key] = known_p_values.get(claim_key.split('-')[0], claim_key.split('-')[0])

# Save the reformatted and readable claims to a JSON file
with open('./wikidata-links.json', 'w') as f:
    json.dump(reformatted_claims, f, indent=4, ensure_ascii=False)
