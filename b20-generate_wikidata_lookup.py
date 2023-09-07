
import sqlite3
import json

def main():
    # Connect to the database
    conn = sqlite3.connect('./kweb.db')

    # Execute a query and fetch all results
    def execute_query(query, connection):
        cursor = connection.execute(query)
        return cursor.fetchall()

    # Extract relevant data from 'nodes' table
    nodes_query = "SELECT name, wikidataId FROM nodes WHERE wikidataId IS NOT NULL;"
    nodes_data = execute_query(nodes_query, conn)

    # Extract relevant data from 'metadata' table
    metadata_query = "SELECT id, name, alias FROM metadata;"
    metadata_data = execute_query(metadata_query, conn)

    # Create a mapping from metadata id to wikidataId using 'nodes' table
    metadata_to_wikidata = {}
    metadata_id_query = "SELECT id, wikidataId FROM nodes;"
    metadata_id_data = execute_query(metadata_id_query, conn)

    for id_, wikidataId in metadata_id_data:
        if wikidataId:
            metadata_to_wikidata[id_] = wikidataId

    # Close the connection
    conn.close()

    # Create wikidata-lookup dictionary
    wikidata_lookup = {}
    metadata_name_count = 0
    metadata_alias_count = 0

    # Populate with data from 'nodes'
    for name, wikidataId in nodes_data:
        wikidata_lookup[name] = wikidataId

    # Populate with data from 'metadata'
    for id_, name, alias in metadata_data:
        wikidataId = metadata_to_wikidata.get(id_)
        if wikidataId:
            if name not in wikidata_lookup:
                wikidata_lookup[name] = wikidataId
                metadata_name_count += 1

            if alias:
                aliases = alias.split('|')
                for alias_name in aliases:
                    if alias_name not in wikidata_lookup:
                        wikidata_lookup[alias_name] = wikidataId
                        metadata_alias_count += 1

    # Save to a JSON file
    with open('./wikidata-lookup.json', 'w') as f:
        json.dump(wikidata_lookup, f, indent=4)

    print(f"The nodes table contributed {len(nodes_data)} entries.")
    print(f"The metadata table added {len(metadata_data)} entries.")
    print(f"From the metadata table, {metadata_name_count} entries came from the name column and {metadata_alias_count} entries from the alias column.")
    print(f"The final JSON file contains {len(wikidata_lookup)} unique entries.")

if __name__ == "__main__":
    main()
