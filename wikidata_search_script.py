
import json
import requests
import sqlite3

# Initialize or load Wikidata ID cache
wikidata_cache_file = "./.wikidata-search-cache.json"
try:
    with open(wikidata_cache_file, 'r') as f:
        wikidata_cache = json.load(f)
except FileNotFoundError:
    wikidata_cache = {}

def fetch_wikidata_id(wikilink):
    if wikilink in wikidata_cache:
        return wikidata_cache[wikilink]
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageprops",
        "titles": wikilink.split('/')[-1].replace('_', ' ')
    }
    api_url = "https://en.wikipedia.org/w/api.php"
    response = requests.get(api_url, params=params)
    data = response.json()
    page = next(iter(data["query"]["pages"].values()))
    wikidata_id = page.get("pageprops", {}).get("wikibase_item")
    if wikidata_id:
        wikidata_cache[wikilink] = wikidata_id
    return wikidata_id

# Connect to SQLite database
db_path = './kweb.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add 'wikidataId' column if not exists
cursor.execute("PRAGMA table_info(nodes);")
if 'wikidataId' not in [column[1] for column in cursor.fetchall()]:
    cursor.execute("ALTER TABLE nodes ADD COLUMN wikidataId TEXT;")

# Fetch nodes with missing wikidataId
cursor.execute("SELECT id, wikilink FROM nodes WHERE wikidataId IS NULL AND wikilink IS NOT NULL;")
missing_wikidata_ids = cursor.fetchall()

found_count = 0
not_found_count = 0

# Iterate through nodes and fetch Wikidata ID
for node_id, wikilink in missing_wikidata_ids:
    wikidata_id = fetch_wikidata_id(wikilink)
    if wikidata_id:
        cursor.execute("UPDATE nodes SET wikidataId = ? WHERE id = ?;", (wikidata_id, node_id))
        found_count += 1
    else:
        not_found_count += 1

# Commit changes to the database
conn.commit()

# Update the Wikidata ID cache file
with open(wikidata_cache_file, 'w') as f:
    json.dump(wikidata_cache, f)

# Print debug information
print(f"Found {found_count} missing Wikidata IDs.")
print(f"Could not find {not_found_count} Wikidata IDs.")
print(f"Total nodes with missing Wikidata IDs: {len(missing_wikidata_ids)}")
