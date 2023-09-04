import sqlite3
import requests
import json
import zipfile
import os
import time

def initialize_db():
    db_path = './kweb.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return cursor

def initialize_zip():
    zip_path = './wikidata-cache.zip'
    if not os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            pass
    return zip_path

def wikidata_lookup(wikidata_id):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    try:
        response = requests.get(url)
        return json.loads(response.text) if response.status_code == 200 else None
    except Exception as e:
        print(f"Exception for {wikidata_id}: {e}")
        return None

def rate_limit(last_request_time, interval=1.0):
    current_time = time.time()
    elapsed_time = current_time - last_request_time
    if elapsed_time < interval:
        time.sleep(interval - elapsed_time)
    return current_time

def main():
    cursor = initialize_db()
    zip_path = initialize_zip()
    last_request_time = 0.0

    cursor.execute("SELECT DISTINCT wikidataId FROM nodes WHERE wikidataId IS NOT NULL;")
    rows = cursor.fetchall()
    total_ids = len(rows)
    processed_ids = 0

    for row in rows:
        wikidata_id = row[0]

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            if f"{wikidata_id}.json" in zipf.namelist():
                print(".", end="", flush=True)
                processed_ids += 1
                continue

        last_request_time = rate_limit(last_request_time)

        wikidata_json = wikidata_lookup(wikidata_id)
        if wikidata_json:
            with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr(f"{wikidata_id}.json", json.dumps(wikidata_json))

        processed_ids += 1
        progress = (processed_ids / total_ids) * 100
        if progress % 10 == 0:
            print(f"\n{int(progress)}% processed...")

        print(".", end="", flush=True)

    print("\nFinished.")


if __name__ == "__main__":
    main()
