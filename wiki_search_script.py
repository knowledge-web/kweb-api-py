
import json
import requests
import sqlite3

# Initialize or load cache
cache_file = "./.wiki-search-cache.json"
try:
    with open(cache_file, 'r') as f:
        cache = json.load(f)
except FileNotFoundError:
    cache = {}

def wikipedia_search(query):
    if query in cache:
        return cache[query]
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query
    }
    response = requests.get(search_url, params=params)
    data = response.json()
    if data.get("query", {}).get("search"):
        page_title = data["query"]["search"][0]["title"]
        wiki_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        cache[query] = wiki_url
        return wiki_url
    return None

# Connect to SQLite database
db_path = './kweb.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch nodes with missing wikilink
cursor.execute("SELECT id, name FROM nodes WHERE wikilink IS NULL;")
missing_wikilinks = cursor.fetchall()

found_count = 0
not_found_count = 0

# Iterate through nodes and search Wikipedia
for node_id, node_name in missing_wikilinks:
    wikilink = wikipedia_search(node_name)
    if wikilink is None:
        cursor.execute("SELECT name, alias FROM metadata WHERE id = ?;", (node_id,))
        metadata = cursor.fetchone()
        if metadata:
            metadata_name, metadata_alias = metadata
            wikilink = wikipedia_search(metadata_name) or wikipedia_search(metadata_alias)
    if wikilink:
        cursor.execute("UPDATE nodes SET wikilink = ? WHERE id = ?;", (wikilink, node_id))
        found_count += 1
    else:
        not_found_count += 1

# Commit changes to the database
conn.commit()

# Update the cache file
with open(cache_file, 'w') as f:
    json.dump(cache, f)

# Print debug information
print(f"Found {found_count} missing wikilinks.")
print(f"Could not find {not_found_count} wikilinks.")
print(f"Total nodes with missing wikilinks: {len(missing_wikilinks)}")
