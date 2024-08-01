import sqlite3

def patch_database(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Add a new table
    c.execute('''CREATE TABLE IF NOT EXISTS new_table
                (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)''')

    # Add a new column to an existing table
    c.execute('''ALTER TABLE data ADD COLUMN new_column TEXT''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    patch_database('database.db')