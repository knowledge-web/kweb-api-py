import json
import requests
import argparse
from urllib.parse import urlparse, unquote

def extract_wiki_title(full_url):
    parsed_url = urlparse(full_url)
    if 'wikipedia.org' in parsed_url.netloc:
        path_elements = parsed_url.path.split('/')
        if len(path_elements) > 2:
            return unquote(path_elements[2])
    return None

def get_wikidata_id(wiki_url):
    wiki_title = extract_wiki_title(wiki_url)
    if not wiki_title:
        print(f"Could not extract Wikipedia title from URL: {wiki_url}")
        return None, False

    print(f"Fetching Wikidata ID for {wiki_title}...")
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&titles={wiki_title}"
    response = requests.get(url)
    data = response.json()
    page = next(iter(data["query"]["pages"].values()))
    wikidata_id = page.get("pageprops", {}).get("wikibase_item", None)
    
    if wikidata_id:
        print(f"Found Wikidata ID: {wikidata_id}")
        return wikidata_id, True
    else:
        print("No Wikidata ID found.")
        return None, False

def add_wikidata_ids(filename):
    total_entries = 0
    entries_with_wikilink = 0
    entries_with_wikidataId = 0
    successful_fetches = 0
    failed_fetches = 0

    print(f"Reading data from {filename}...")
    with open(filename, 'r') as f:
        data = json.load(f)

    for entry in data:
        total_entries += 1
        wikilink = entry.get("wikilink", "")
        
        if wikilink:
            entries_with_wikilink += 1

            if "wikidataId" not in entry:
                wikidata_id, success = get_wikidata_id(wikilink)
                if success:
                    successful_fetches += 1
                    entry["wikidataId"] = wikidata_id
                else:
                    failed_fetches += 1
            else:
                entries_with_wikidataId += 1

    print(f"Updating {filename} with Wikidata IDs...")
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    print("Update complete.")
    print(f"Total entries: {total_entries}")
    print(f"Entries with wikilink: {entries_with_wikilink}")
    print(f"Entries with Wikidata ID: {entries_with_wikidataId}")
    print(f"Successful API fetches: {successful_fetches}")
    print(f"Failed API fetches: {failed_fetches}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add Wikidata IDs to JSON entries.")
    parser.add_argument("--filename", default="old.json", help="JSON file to update")
    args = parser.parse_args()

    add_wikidata_ids(args.filename)
