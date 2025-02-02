import sqlite3
from flask import g

DATABASE = 'pool.db'

def get_db():
    """Connect to the SQLite database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Rows behave like dictionaries
    return db

def create_user(username, email, password_hash):
    """Insert a new user into the database."""
    db = get_db()
    db.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )
    db.commit()

def close_connection():
    """Close the database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Other database helper functions...

# get specific pool
def get_pool(pool_id):
    db = get_db()
    return db.execute("SELECT * FROM pools WHERE id = ?", (pool_id,)).fetchone()

# get all pools
def get_pools():
    db = get_db()
    try:
        pools = db.execute("SELECT * FROM pools").fetchall()
        return pools
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"General error: {e}")
        return []

# show user pools
def user_pools(user_id):
    db = get_db()
    try:
        pools = db.execute("SELECT * FROM pools WHERE owner_id = ?", (user_id,)).fetchall()
        return pools
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"General error: {e}")
        return []

def get_squares(pool_id):
    db = get_db()
    squares = db.execute("SELECT x, y, user_id FROM squares WHERE pool_id = ?", (pool_id,)).fetchall()
    grid_size = db.execute("SELECT grid_size FROM pools WHERE id = ?", (pool_id,)).fetchone()['grid_size']
    grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
    for square in squares:
        grid[square['x']][square['y']] = square['user_id']
    return grid


def claim_square(pool_id, x, y, name):
    db = get_db()
    db.execute(
        "UPDATE squares SET user_id = ? WHERE pool_id = ? AND x = ? AND y = ?",
        (name, pool_id, x, y)
    )
    db.commit()

#delete pool
def delete_pool(pool_id):
    db = get_db()
    db.execute("DELETE FROM pools WHERE id = ?", (pool_id,))
    db.commit()    