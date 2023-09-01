
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

# Query to get list of entities with WikiData IDs (Corrected table name to nodes)
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
        with open(os.path.join(cache_folder, file_name), 'r') as f:
            data = json.load(f)
        
        # Extract WikiData ID from file name
        entity_id = file_name.replace(".json", "")
        
        # Loop through claims to find relationships
        if 'claims' in data:
            for prop, claims in data['claims'].items():
                for claim in claims:
                    # Extract related WikiData ID if exists
                    if 'mainsnak' in claim and 'datavalue' in claim['mainsnak'] and 'value' in claim['mainsnak']['datavalue']:
                        related_id = claim['mainsnak']['datavalue']['value'].get('id', None)
                        if related_id:
                            # Update database
                            cursor.execute("INSERT OR IGNORE INTO links (source, target) VALUES (?, ?)", (entity_id, related_id))
                            print(f"Added link from {entity_id} to {related_id}")

# Call the cross_reference_and_update function
cross_reference_and_update()

# Commit database changes
conn.commit()

# Close the database connection
conn.close()

# Print summary
print(f"Searched: {searched_count}, Found: {found_count}, Cached Files: {len(os.listdir(cache_folder))}")
