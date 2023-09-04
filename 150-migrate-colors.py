
import sqlite3

# Function to get column names of a table
def get_column_names(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    return [column[1] for column in cursor.fetchall()]

# Function to convert a signed integer to an unsigned integer
def signed_to_unsigned(signed):
    return signed & 0xFFFFFFFF

# Function to convert ARGB to RGB
def argb_to_rgb(argb):
    unsigned = signed_to_unsigned(argb)
    blue = unsigned & 0xFF
    green = (unsigned >> 8) & 0xFF
    red = (unsigned >> 16) & 0xFF
    return (red, green, blue)

# Function to convert color to RGB string format
def color_to_rgb_str(color):
    if color is None:
        return None
    rgb_tuple = argb_to_rgb(int(color))
    return f"rgb({rgb_tuple[0]},{rgb_tuple[1]},{rgb_tuple[2]})"

# Connect to the Brain_Updated.db
conn_brain = sqlite3.connect('Brain.db')
cursor_brain = conn_brain.cursor()

# Connect to the kweb.db
conn_kweb = sqlite3.connect('kweb.db')
cursor_kweb = conn_kweb.cursor()

# Check if color and bgcolor columns exist in nodes table, if not, add them
nodes_columns = get_column_names(cursor_kweb, 'nodes')
if 'color' not in nodes_columns:
    cursor_kweb.execute("ALTER TABLE nodes ADD COLUMN color TEXT;")
if 'bgcolor' not in nodes_columns:
    cursor_kweb.execute("ALTER TABLE nodes ADD COLUMN bgcolor TEXT;")

# Check if color column exists in links table, if not, add it
links_columns = get_column_names(cursor_kweb, 'links')
if 'color' not in links_columns:
    cursor_kweb.execute("ALTER TABLE links ADD COLUMN color TEXT;")

# Fetch color-related data from thoughts and links in Brain_Updated.db
cursor_brain.execute("SELECT Id, ForegroundColor, BackgroundColor FROM thoughts")
thoughts_colors_data = cursor_brain.fetchall()

cursor_brain.execute("SELECT Id, Color FROM links")
links_colors_data = cursor_brain.fetchall()

# Convert thoughts colors to RGB string format
thoughts_colors_rgb = [(id_, color_to_rgb_str(foreground), color_to_rgb_str(background)) for id_, foreground, background in thoughts_colors_data]

# Convert links colors to RGB string format
links_colors_rgb = [(id_, color_to_rgb_str(color)) for id_, color in links_colors_data]

# Update nodes and links tables in kweb.db
update_nodes_color_query = "UPDATE nodes SET color = ?, bgcolor = ? WHERE Id = ?"
update_links_color_query = "UPDATE links SET color = ? WHERE source = ? AND target = ?"

# Batch update nodes
cursor_kweb.executemany(update_nodes_color_query, thoughts_colors_rgb)

# Batch update links
links_batch_data = [(color, thought_id_a, thought_id_b) for id_, color in links_colors_rgb for thought_id_a, thought_id_b in [id_.split('-', 1)]]
cursor_kweb.executemany(update_links_color_query, links_batch_data)

# Commit changes to kweb.db
conn_kweb.commit()

# Close the database connections
conn_brain.close()
conn_kweb.close()
