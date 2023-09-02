import sqlite3
import json

# Initialize counters
searched_count = 0
found_count = 0

# Read old-links.json
with open('./old-links.json', 'r') as f:
    old_links = json.load(f)

# Connect to SQLite database
conn = sqlite3.connect('./kweb.db')
cursor = conn.cursor()

# Select links with missing or null names and both source and target have wikidataId
cursor.execute("""
        SELECT source, target
        FROM links
        WHERE (name IS NULL OR name = '')
        AND source IN (SELECT id FROM nodes WHERE wikidataId IS NOT NULL)
        AND target IN (SELECT id FROM nodes WHERE wikidataId IS NOT NULL)
    """)

# Iterate over the selected rows
for row in cursor.fetchall():
    source, target = row
    searched_count += 1

    # Get wikidataId for source and target nodes
    cursor.execute("SELECT wikidataId FROM nodes WHERE id = ?", (source,))
    source_wikidataId = cursor.fetchone()[0]

    cursor.execute("SELECT wikidataId FROM nodes WHERE id = ?", (target,))
    target_wikidataId = cursor.fetchone()[0]

    # Build the key to search in old-links.json
    key = f'{source_wikidataId}-{target_wikidataId}'

    print(f'Debug: Searching for key {key} ...')

    # Check if the key exists in old-links.json
    if key in old_links:
        found_count += 1
        new_name = old_links[key]
        print(f'Debug: Found. Updating name to {new_name}.')

        # Update the name in the database
        cursor.execute('UPDATE links SET name = ? WHERE source = ? AND target = ?', (new_name, source, target))
        conn.commit()
    else:
        print('Debug: Not found.')

# Close the database connection
conn.close()

# Print summary
print(f"Searched: {searched_count}, Found: {found_count}")