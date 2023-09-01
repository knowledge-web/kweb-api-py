
import sqlite3
import json
import requests
import os

# Initialize counters
searched_count = 0
found_count = 0
cache_folder = "./wikidata-cache/"

# Create cache folder if it doesn't exist
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

# Connect to SQLite database
conn = sqlite3.connect('./kweb.db')
cursor = conn.cursor()

# Query to get list of entities with WikiData IDs
query = "SELECT id, wikidataId FROM nodes WHERE wikidataId IS NOT NULL"
cursor.execute(query)

# Fetch all rows
rows = cursor.fetchall()

# Function to fetch data from WikiData API
def fetch_wikidata(entity_id):
    global searched_count
    global found_count

    cache_file = f"{cache_folder}{entity_id}.json"

    # Check if data is already cached
    if os.path.exists(cache_file):
        print(f"Cache exists for {entity_id}")
        return

    # Fetch data from WikiData API
    url = f"https://www.wikidata.org/w/api.php?action=wbgetclaims&entity={entity_id}&format=json"
    response = requests.get(url)

    # Cache the response
    if response.status_code == 200:
        searched_count += 1
        with open(cache_file, "w") as f:
            json.dump(response.json(), f)
        print(f"Cached data for {entity_id}")
        found_count += 1
    else:
        print(f"Failed to fetch data for {entity_id}")

# Loop through entities and fetch data
for row in rows:
    fetch_wikidata(row[1])


# Function to cross-reference and update database
def cross_reference_and_update():
    global cache_folder
    global conn
    global cursor

    # Loop through each cached file
    for file_name in os.listdir(cache_folder):
        # Load the cached data
        try:
            with open(os.path.join(cache_folder, file_name), 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading cache file {file_name}: {e}")
            continue

        # Extract WikiData ID from file name
        entity_id = file_name.replace(".json", "")

        # Check for 'claims' in data
        if 'claims' not in data:
            print(f"No claims found for entity {entity_id}.")
            continue

        # Loop through claims to find relationships
        for prop, claims in data['claims'].items():
            for claim in claims:
                # Check for required fields and their types
                if 'mainsnak' not in claim or 'datavalue' not in claim['mainsnak'] or 'value' not in claim['mainsnak']['datavalue']:
                    print(f"Required fields missing for claim in entity {entity_id}.")
                    continue

                value = claim['mainsnak']['datavalue']['value']
                related_id = None

                # Check the type of 'value' and assign related_id accordingly
                if isinstance(value, dict):
                    related_id = value.get('id', None)
                elif isinstance(value, str):
                    related_id = value
                else:
                    print(f"Unsupported type {type(value)} for value in entity {entity_id}.")
                    continue

                # Update database if related_id is found
                if related_id:
                    cursor.execute("INSERT OR IGNORE INTO links (source, target) VALUES (?, ?)", (entity_id, related_id))
                    print(f"Added link from {entity_id} ({data.get('labels', {}).get('en', {}).get('value', 'Unknown')}) to {related_id}.")


# Call the cross_reference_and_update function
cross_reference_and_update()

# Commit database changes
conn.commit()

# Close the database connection
conn.close()

# Print summary
print(f"Searched: {searched_count}, Found: {found_count}, Cached Files: {len(os.listdir(cache_folder))}")
