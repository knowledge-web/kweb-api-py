
import json
import requests
from time import sleep

def fetch_wikidata_id(query):
    try:
        url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": query
        }
        response = requests.get(url, params=params)
        results = response.json().get("search", [])
        if results:
            return results[0].get("id")
        else:
            return None
    except Exception as e:
        print(f"Error fetching ID for {query}: {e}")
        return None

def main():
    # Load the JSON file
    with open("entities.json", "r") as f:
        data = json.load(f)
    
    successes = 0
    failures = 0
    
    # Loop through entities and populate missing wikidataIds
    for entity, wikidata_id in data.items():
        if wikidata_id is None:
            new_id = fetch_wikidata_id(entity)
            if new_id:
                data[entity] = new_id
                print(".", end="", flush=True)
                successes += 1
            else:
                print("-", end="", flush=True)
                failures += 1
            sleep(0.5)  # To avoid rate-limiting
    
    # Update the JSON file
    with open("entities.json", "w") as f:
        json.dump(data, f)
    
    print(f"\nCompleted. Successes: {successes}, Failures: {failures}")

if __name__ == "__main__":
    main()
