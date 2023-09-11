
import json
import sqlite3
import os

# Initialize counters for summary
updated_date_count = 0
updated_location_count = 0

# Function to safely extract birth and death dates
def extract_nested_dates_safe(wikidataId, directory):
    # ... (Code for date extraction)

# Function to extract birth place, death place, and places lived
def extract_places(wikidataId, directory):
    # ... (Code for place extraction)

# Load location details
with open('./wikidata-locations.json', 'r') as json_file:
    wikidata_locations = json.load(json_file)

# Connect to SQLite database
conn = sqlite3.connect('./kweb.db')
cursor = conn.cursor()

# Conditionally add new columns for dates and location details
# ... (Code for adding columns)

# Update table with date and location information
cursor.execute("SELECT id, wikidataId FROM nodes WHERE wikidataId IS NOT NULL;")
all_rows = cursor.fetchall()

for row_id, wikidata_id in all_rows:
    # ... (Code for updating the table)
    
    if birthdate or deathdate:
        updated_date_count += 1
    if birth_place_details or death_place_details or places_lived_details:
        updated_location_count += 1

conn.commit()
conn.close()

# Print the summary of successful inserts
print(f'Updated dates for {updated_date_count} entries.')
print(f'Updated locations for {updated_location_count} entries.')
