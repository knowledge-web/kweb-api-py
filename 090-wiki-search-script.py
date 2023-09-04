
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

api_count = 0
cache_count = 0

def wikipedia_search(query):
    global api_count, cache_count
    if query in cache:
        cache_count += 1
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
        api_count += 1
        page_title = data["query"]["search"][0]["title"]
        wiki_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        cache[query] = wiki_url
        print(f"API call for {query} successful.")
        return wiki_url
    print(f"API call for {query} returned no result.")
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
print(f"API calls made: {api_count}")
print(f"Cache hits: {cache_count}")
print(f"Total entries tried: {len(missing_wikilinks)}")
print(f"Total entries found: {found_count}")
