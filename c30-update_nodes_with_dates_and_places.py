
import json
import sqlite3
import os

# Your existing functions for date extraction can go here...

def extract_places(wikidataId, directory):
    file_path = os.path.join(directory, f"{wikidataId}.json")
    birth_place, death_place, places_lived = None, None, []
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            claims = data.get('entities', {}).get(wikidataId, {}).get('claims', {})
            birth_claim = claims.get('P19', [{}])[0].get('mainsnak', {})
            birth_place = birth_claim.get('datavalue', {}).get('value', {}).get('id', None)
            death_claim = claims.get('P20', [{}])[0].get('mainsnak', {})
            death_place = death_claim.get('datavalue', {}).get('value', {}).get('id', None)
            lived_claims = claims.get('P551', [])
            for lived_claim in lived_claims:
                place_lived = lived_claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', None)
                if place_lived:
                    places_lived.append(place_lived)
    except FileNotFoundError:
        pass
    return birth_place, death_place, places_lived

# Load location details (You can load your JSON file with location details here)
with open('./wikidata-locations.json', 'r') as json_file:
    wikidata_locations = json.load(json_file)

# Connect to SQLite database
conn = sqlite3.connect('./kweb.db')
cursor = conn.cursor()

# Your existing code for adding date columns can go here...

# Conditionally add new columns for location details
location_columns_to_add = ['birthplace TEXT', 'deathplace TEXT', 'places TEXT']
cursor.execute("PRAGMA table_info(nodes);")
existing_columns = [column[1] for column in cursor.fetchall()]
for column in location_columns_to_add:
    column_name = column.split(' ')[0]
    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE nodes ADD COLUMN {column};")

conn.commit()

# Your existing code for updating date columns can go here...

# Update table with location information
cursor.execute("SELECT id, wikidataId FROM nodes WHERE wikidataId IS NOT NULL;")
all_rows = cursor.fetchall()
for row_id, wikidata_id in all_rows:
    birth_place, death_place, places_lived = extract_places(wikidata_id, '/tmp')
    birth_place_details = json.dumps(wikidata_locations.get(birth_place, {}))
    death_place_details = json.dumps(wikidata_locations.get(death_place, {}))
    places_lived_details = json.dumps([wikidata_locations.get(place, {}) for place in places_lived])
    if birth_place_details or death_place_details or places_lived_details:
        cursor.execute("UPDATE nodes SET birthplace = ?, deathplace = ?, places = ? WHERE id = ?", (birth_place_details, death_place_details, places_lived_details, row_id))

conn.commit()
conn.close()
