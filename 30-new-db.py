
import sqlite3
import sys

def create_new_db_adjusted(src_db_path, dest_db_path):
    src_conn = sqlite3.connect(src_db_path)
    dest_conn = sqlite3.connect(dest_db_path)
    src_cursor = src_conn.cursor()
    dest_cursor = dest_conn.cursor()
    
    dest_cursor.execute("""
        CREATE TABLE nodes (
            Id TEXT PRIMARY KEY,
            Name TEXT,
            Label TEXT,
            TypeId TEXT
        )
    """)
    
    src_cursor.execute("SELECT Id, Name, Label, TypeId FROM thoughts")
    rows = src_cursor.fetchall()
    dest_cursor.executemany("INSERT INTO nodes (Id, Name, Label, TypeId) VALUES (?, ?, ?, ?)", rows)
    
    dest_cursor.execute("""
        CREATE TABLE links (
            name TEXT,
            source TEXT,
            target TEXT,
            FOREIGN KEY (source) REFERENCES nodes (Id),
            FOREIGN KEY (target) REFERENCES nodes (Id)
        )
    """)
    
    src_cursor.execute("SELECT Name, ThoughtIdA, ThoughtIdB FROM links")
    rows = src_cursor.fetchall()
    dest_cursor.executemany("INSERT INTO links (name, source, target) VALUES (?, ?, ?)", rows)
    
    dest_conn.commit()
    src_conn.close()
    dest_conn.close()

if __name__ == '__main__':
    src_db_path = sys.argv[1] if len(sys.argv) > 1 else 'Brain.db'
    dest_db_path = sys.argv[2] if len(sys.argv) > 2 else 'kweb.db'
    create_new_db_adjusted(src_db_path, dest_db_path)
