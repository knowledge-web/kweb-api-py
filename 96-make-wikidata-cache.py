import sqlite3
import requests
import json
import zipfile
import os
import time

# Initialize database connection
db_path = './kweb.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Initialize zip file for caching WikiData responses
zip_path = './wikidata-cache.zip'
if not os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pass

# Function to perform WikiData lookup
def wikidata_lookup(wikidata_id):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Error for {wikidata_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception for {wikidata_id}: {e}")
        return None

# Rate-limiting: 1 request per second
rate_limit_interval = 1.0
last_request_time = 0.0

# Main loop
cursor.execute("SELECT DISTINCT wikidataId FROM nodes WHERE wikidataId IS NOT NULL;")
for row in cursor.fetchall():
    wikidata_id = row[0]
    
    # Check if already in cache
    already_cached = False
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        if f"{wikidata_id}.json" in zipf.namelist():
            already_cached = True
    
    if already_cached:
        print(".", end="", flush=True)
        continue
    
    # Respect rate limits
    current_time = time.time()
    time_since_last_request = current_time - last_request_time
    if time_since_last_request < rate_limit_interval:
        time.sleep(rate_limit_interval - time_since_last_request)
    
    # Perform lookup and save to cache
    wikidata_json = wikidata_lookup(wikidata_id)
    if wikidata_json:
        with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(f"{wikidata_id}.json", json.dumps(wikidata_json))
    
    # Update last request time
    last_request_time = time.time()
    print(".", end="", flush=True)

print("\nFinished.")
