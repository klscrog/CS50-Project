from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
import slqite3

app = Flask(__name__)
DATABASE = 'pool.db'

def get_db():
    """Connect to the database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()