import sqlite3

def update_kweb_links_filtered(conn_kweb, filtered_brain_links):
    cursor_kweb = conn_kweb.cursor()
    updated_count = 0
    
    # Remove all names from the kweb (2).db links table
    cursor_kweb.execute("UPDATE links SET name = NULL;")
    conn_kweb.commit()
    
    for thought_a, thought_b, name, type_name in filtered_brain_links:
        update_name = name if name else type_name
        
        cursor_kweb.execute("""
            UPDATE links 
            SET name = ? 
            WHERE source = ? AND target = ?;
        """, (update_name, thought_a, thought_b))
        
        updated_count += cursor_kweb.rowcount
    
    conn_kweb.commit()
    return updated_count

# Connect to the databases
conn_brain = sqlite3.connect('Brain.db')
conn_kweb = sqlite3.connect('kweb.db')

# Fetch records from Brain_Updated.db with either Name or TypeName
cursor_brain = conn_brain.cursor()
cursor_brain.execute("SELECT ThoughtIdA, ThoughtIdB, Name, TypeName FROM links WHERE Name IS NOT NULL OR TypeName IS NOT NULL;")
all_brain_links_with_name_or_type = cursor_brain.fetchall()

# Filter out records where both Name and TypeName are None or empty
all_brain_links_with_name_or_type = [record for record in all_brain_links_with_name_or_type if record[2] or record[3]]

# Update kweb (2).db
updated_count_filtered = update_kweb_links_filtered(conn_kweb, all_brain_links_with_name_or_type)
print(f"Updated {updated_count_filtered} records.")
