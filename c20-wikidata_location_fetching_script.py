
import json
import time
import requests

# Function to fetch location details from Wikidata
def fetch_location_details(location_id):
    try:
        url = f"https://www.wikidata.org/wiki/Special:EntityData/{location_id}.json"
        response = requests.get(url)
        data = response.json()
        
        # Logic to extract place name
        entity = data.get("entities", {}).get(location_id, {})
        labels = entity.get("labels", {}).get("en", {}).get("value", "")

        # Logic to extract country (P17 is the property for 'country')
        claims = entity.get("claims", {})
        country_claim = claims.get("P17", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
        country = "Unknown" if not country_claim else country_claim  # Replace this with actual country name fetched from another API call if necessary
        
        # Logic to extract coordinates (P625 is the property for 'coordinate location')
        coordinates_claim = claims.get("P625", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", {})
        latitude = coordinates_claim.get("latitude", 0.0)
        longitude = coordinates_claim.get("longitude", 0.0)
        coordinates = [latitude, longitude]

        return {
            'name': labels,
            'country': country,  # This will be the country's Wikidata ID, not its name
            'coordinates': coordinates
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Read the previously generated JSON to continue from where it left off
try:
    with open('wikidata-locations.json', 'r') as f:
        location_details = json.load(f)
except FileNotFoundError:
    location_details = {}

# Initialize counters for logging
successful_fetches = 0
failed_fetches = 0

# Fetching details for all location IDs
for location_id, details in location_details.items():
    # Skip already fetched IDs
    if details is not None:
        continue

    fetched_details = fetch_location_details(location_id)
    if fetched_details is not None:
        location_details[location_id] = fetched_details
        print('.', end='', flush=True)
        successful_fetches += 1
    else:
        print('-', end='', flush=True)
        failed_fetches += 1

    # Save progress to JSON file
    with open('wikidata-locations.json', 'w') as f:
        json.dump(location_details, f)

    # Simulate API rate limiting (remove in a real-world scenario)
    time.sleep(0.1)

print(f"\nCompleted fetching. Successful: {successful_fetches}, Failed: {failed_fetches}")
