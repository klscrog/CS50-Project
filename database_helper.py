import sqlite3
from flask import g
from datetime import datetime

DATABASE = 'pool.db'

def get_db():
    """Connect to the SQLite database."""
    db = getattr(g, '_database', None)
    if db is None:
         # Increase timeout to 30 seconds, Rows behave like dictionaries
        db = g._database = sqlite3.connect(DATABASE, timeout=30)  
        db.row_factory = sqlite3.Row  
    return db

def close_connection(exception):
    """Close the database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def handle_db_error(e):
    print(f"Database error: {e}")
    return []

def handle_general_error(e):
    print(f"General error: {e}")
    return []

def create_user(username, email, password_hash):
    """Insert a new user into the database."""
    db = get_db()
    db.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )
    db.commit()

def get_pool(pool_id):
    """Get a specific pool by ID."""
    db = get_db()
    pool = db.execute("SELECT * FROM pools WHERE id = ?", (pool_id,)).fetchone()
    if pool:
        pool = dict(pool)  # Convert sqlite3.Row to dictionary
        pool['created_at'] = datetime.strptime(pool['created_at'], '%Y-%m-%d %H:%M:%S')
    return pool

def get_pools():
    """Get all pools."""
    db = get_db()
    try:
        pools = db.execute("SELECT * FROM pools").fetchall()
        return pools
    except sqlite3.Error as e:
        return handle_db_error(e)
    except Exception as e:
        return handle_general_error(e)

def user_pools(user_id):
    db = get_db()
    try:
        pools = db.execute("SELECT * FROM pools WHERE owner_id = ?", (user_id,)).fetchall()
        return pools
    except sqlite3.Error as e:
        return handle_db_error(e)
    except Exception as e:
        return handle_general_error(e)

def get_squares(pool_id):
    """Get all squares for a specific pool."""
    db = get_db()
    squares = db.execute("SELECT x, y, name FROM squares WHERE pool_id = ?", (pool_id,)).fetchall()
    grid_size = db.execute("SELECT grid_size FROM pools WHERE id = ?", (pool_id,)).fetchone()['grid_size']
    grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
    for square in squares:
        grid[square['x']][square['y']] = square['name']
    return grid

def claim_square(pool_id, x, y, name):
    db = get_db()
    db.execute(
        "UPDATE squares SET name = ? WHERE pool_id = ? AND x = ? AND y = ?",
        (name, pool_id, x, y)
    )
    db.commit()

def delete_pool(pool_id):
    db = get_db()
    db.execute("DELETE FROM pools WHERE id = ?", (pool_id,))
    db.commit()