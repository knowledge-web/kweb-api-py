import json
import sqlite3

def populate_json_with_wikidata_ids_from_txt(txt_file_path, db_path, updated_json_file_path):
    # Load the entities from the text file
    with open(txt_file_path, 'r') as f:
        lines = f.readlines()
    sorted_entities = {line.strip(): None for line in lines}

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Initialize counters
    nodes_counter = 0
    metadata_name_counter = 0
    metadata_alias_counter = 0
    not_found_counter = 0

    # Iterate through the keys and update values with Wikidata IDs
    for key in sorted_entities.keys():
        cursor.execute("SELECT wikidataId FROM nodes WHERE LOWER(name) = LOWER(?) AND wikidataId IS NOT NULL", (key,))
        result = cursor.fetchone()
        
        if result:
            sorted_entities[key] = result[0]
            nodes_counter += 1
        else:
            cursor.execute("SELECT wikidataId FROM metadata INNER JOIN nodes ON metadata.id = nodes.id WHERE LOWER(metadata.name) = LOWER(?) AND wikidataId IS NOT NULL", (key,))
            result = cursor.fetchone()
            
            if result:
                sorted_entities[key] = result[0]
                metadata_name_counter += 1
            else:
                cursor.execute("SELECT wikidataId FROM metadata INNER JOIN nodes ON metadata.id = nodes.id WHERE LOWER(metadata.alias) = LOWER(?) AND wikidataId IS NOT NULL", (key,))
                result = cursor.fetchone()
                
                if result:
                    sorted_entities[key] = result[0]
                    metadata_alias_counter += 1
                else:
                    not_found_counter += 1

    # Close the database connection
    conn.close()

    # Save the updated JSON file
    with open(updated_json_file_path, 'w') as f:
        json.dump(sorted_entities, f)

    # Show statistics
    print(f"Found in nodes table: {nodes_counter}")
    print(f"Found in metadata.name: {metadata_name_counter}")
    print(f"Found in metadata.alias: {metadata_alias_counter}")
    print(f"Not found: {not_found_counter}")

# Example usage
if __name__ == "__main__":
    txt_file_path = "./entities.txt"
    db_path = "kweb.db"
    updated_json_file_path = "entities.json"
    
    populate_json_with_wikidata_ids_from_txt(txt_file_path, db_path, updated_json_file_path)
  