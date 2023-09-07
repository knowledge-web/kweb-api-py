
# Import required libraries
import json
import requests

# Initialize variables to keep track of successes and failures
success_count = 0
failure_count = 0

# Load the existing JSON file
try:
    with open('./wikidata-lookup.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print("File not found. Please make sure wikidata-lookup.json exists in the same directory.")
    exit(1)

# Function to search WikiData for a specific key and return the ID or an empty string
def search_wikidata(key):
    search_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={key}&language=en&format=json"
    try:
        response = requests.get(search_url)
        search_results = response.json()
        if 'search' in search_results and len(search_results['search']) > 0:
            return search_results['search'][0]['id']
        else:
            return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

# Loop through the data to fill missing wikidataIds
for key, value in data.items():
    if not value:
        wikidata_id = search_wikidata(key)
        if wikidata_id:
            print(".", end="", flush=True)
            success_count += 1
        else:
            print("-", end="", flush=True)
            failure_count += 1
        data[key] = wikidata_id
        # Save the updated JSON file
        with open('./wikidata-lookup.json', 'w') as f:
            json.dump(data, f, indent=4)

# Print summary
print(f"\nTotal successes: {success_count}, Total failures: {failure_count}")
