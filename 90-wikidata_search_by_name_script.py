
import json
import requests
import sqlite3

# Initialize or load Wikidata ID cache by name
wikidata_name_cache_file = "./.wikidata-name-search-cache.json"
try:
    with open(wikidata_name_cache_file, 'r') as f:
        wikidata_name_cache = json.load(f)
except FileNotFoundError:
    wikidata_name_cache = {}

api_count = 0
cache_count = 0

def fetch_wikidata_id_by_name(name):
    global api_count, cache_count
    if name in wikidata_name_cache:
        cache_count += 1
        return wikidata_name_cache[name]
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": name
    }
    api_url = "https://www.wikidata.org/w/api.php"
    response = requests.get(api_url, params=params)
    data = response.json()
    if data.get("search"):
        api_count += 1
        wikidata_id = data["search"][0]["id"]
        wikidata_name_cache[name] = wikidata_id
        print(f"API call for {name} successful.")
        return wikidata_id
    print(f"API call for {name} returned no result.")
    return None

# Connect to SQLite database
db_path = './kweb.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch nodes with missing wikidataId
cursor.execute("SELECT id, name FROM nodes WHERE wikidataId IS NULL;")
missing_wikidata_ids_by_name = cursor.fetchall()

found_count = 0
not_found_count = 0

# Iterate through nodes and fetch Wikidata ID by name
for node_id, node_name in missing_wikidata_ids_by_name:
    wikidata_id = fetch_wikidata_id_by_name(node_name)
    if wikidata_id is None:
        cursor.execute("SELECT name, alias FROM metadata WHERE id = ?;", (node_id,))
        metadata = cursor.fetchone()
        if metadata:
            metadata_name, metadata_alias = metadata
            wikidata_id = fetch_wikidata_id_by_name(metadata_name) or fetch_wikidata_id_by_name(metadata_alias)
    if wikidata_id:
        cursor.execute("UPDATE nodes SET wikidataId = ? WHERE id = ?;", (wikidata_id, node_id))
        found_count += 1
    else:
        not_found_count += 1

# Commit changes to the database
conn.commit()

# Update the Wikidata ID cache file by name
with open(wikidata_name_cache_file, 'w') as f:
    json.dump(wikidata_name_cache, f)

# Print debug information
print(f"Found {found_count} missing Wikidata IDs.")
print(f"Could not find {not_found_count} Wikidata IDs.")
print(f"Total nodes with missing Wikidata IDs: {len(missing_wikidata_ids_by_name)}")
print(f"API calls made: {api_count}")
print(f"Cache hits: {cache_count}")
print(f"Total entries tried: {len(missing_wikidata_ids_by_name)}")
print(f"Total entries found: {found_count}")
