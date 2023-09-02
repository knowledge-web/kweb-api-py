import requests
import sqlite3
import json
import zipfile
import time
import os

def get_wikidata_info(wikidata_id, cache_path):
    # Check if data is already cached
    zip_file_path = f"{cache_path}/{wikidata_id}.json"
    with zipfile.ZipFile(cache_path, 'a') as zipf:
        if wikidata_id + ".json" in zipf.namelist():
            print(".", end="", flush=True)
            return

    # If not cached, fetch data from Wikidata
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: {e}")
        return

    # Cache the response
    with zipfile.ZipFile(cache_path, 'a') as zipf:
        zipf.writestr(f"{wikidata_id}.json", json.dumps(response.json()))
    print(".", end="", flush=True)

def main():
    # Database path
    db_path = "./kweb.db"
    # Cache path
    cache_path = "./wikidata-cache.zip"

    # Create cache zip if it doesn't exist
    if not os.path.exists(cache_path):
        with zipfile.ZipFile(cache_path, 'w'):
            pass

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch nodes with wikidataId
    cursor.execute("SELECT DISTINCT wikidataId FROM nodes WHERE wikidataId IS NOT NULL")
    wikidata_ids = [row[0] for row in cursor.fetchall()]

    # Process each wikidataId
    for wikidata_id in wikidata_ids:
        get_wikidata_info(wikidata_id, cache_path)
        time.sleep(1)  # To respect rate limits

    print("\nProcessing complete.")

if __name__ == "__main__":
    main()
