
import sqlite3

def update_database(db_path="./Brain.db"):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add the 'TypeName' column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE links ADD COLUMN TypeName TEXT;")
        print("Added 'TypeName' column to 'links' table.")
    except sqlite3.OperationalError:
        print("'TypeName' column already exists. Skipping addition.")

    # Convert 'TypeId' to lowercase
    cursor.execute("UPDATE links SET TypeId = LOWER(TypeId) WHERE TypeId IS NOT NULL AND TypeId != '00000000-0000-0000-0000-000000000000';")
    print("Converted 'TypeId' values to lowercase.")

    # Update the 'TypeName' column based on 'TypeId'
    cursor.execute("UPDATE links SET TypeName = (SELECT Name FROM links AS l2 WHERE l2.Id = links.TypeId) WHERE TypeId IS NOT NULL AND TypeId != '00000000-0000-0000-0000-000000000000';")
    print("Updated 'TypeName' column based on 'TypeId'.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_database()
