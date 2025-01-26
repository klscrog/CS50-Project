import sqlite3

def init_db():
    """Initialize the database with the schema."""
    with sqlite3.connect('pool.db') as conn:
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()