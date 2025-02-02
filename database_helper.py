from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for, g
from flask_session import Session
import sqlite3
from authorization_helper import auth_bp, login_required
from database_helper import get_db, get_pool, get_pools, delete_pool, user_pools, get_squares, claim_square, close_connection
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import random
import logging

app = Flask(__name__)
app.secret_key = '123'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Register the auth blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    user_id = session.get("user_id")
    if user_id:
        user_pool_list = user_pools(user_id)
        if not user_pool_list:
            flash("You have not created any pools yet.")
        return render_template('index.html', user_pool_list=user_pool_list)
    else:
        return redirect(url_for('new_session'))

@app.teardown_appcontext
def close_db_connection(exception):
    close_connection(exception)

@app.route('/new_session')
def new_session():
    return render_template('new_session.html')

@app.route('/create_pool', methods=['GET', 'POST'])
def create_pool():
    if request.method == 'POST':
        name = request.form['name']
        grid_size = int(request.form['grid_size'])
        user_id = session.get('user_id')

        if not user_id:
            return redirect(url_for('auth.login'))

        db = get_db()
        db.execute(
            "INSERT INTO pools (name, grid_size, owner_id) VALUES (?, ?, ?)",
            (name, grid_size, user_id)
        )
        pool_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Insert placeholders for the first row and column with '?'
        for i in range(grid_size):
            db.execute(
                "INSERT INTO squares (pool_id, x, y, name) VALUES (?, ?, ?, ?)",
                (pool_id, 0, i, '?')
            )
            db.execute(
                "INSERT INTO squares (pool_id, x, y, name) VALUES (?, ?, ?, ?)",
                (pool_id, i, 0, '?')
            )

        # Insert 'claim' for all internal squares
        for x in range(1, grid_size):
            for y in range(1, grid_size):
                db.execute(
                    "INSERT INTO squares (pool_id, x, y, name) VALUES (?, ?, ?, ?)",
                    (pool_id, x, y, 'claim')
                )

        db.commit()
        return redirect(url_for('index'))

    return render_template('create_pool.html')

@app.route('/generate_numbers/<int:pool_id>', methods=['POST'])
def generate_numbers(pool_id):
    db = get_db()
    pool = get_pool(pool_id)
    grid_size = pool['grid_size']

    if grid_size == 11:
        numbers = list(range(10))
        random.shuffle(numbers)
        for i in range(1, grid_size):
            db.execute(
                "UPDATE squares SET name = ? WHERE pool_id = ? AND x = 0 AND y = ?",
                (numbers[i-1], pool_id, i)
            )
            db.execute(
                "UPDATE squares SET name = ? WHERE pool_id = ? AND x = ? AND y = 0",
                (numbers[i-1], pool_id, i)
            )
    elif grid_size == 6:
        numbers = list(range(10))
        random.shuffle(numbers)
        pairs = [(numbers[i], numbers[i+1]) for i in range(0, 10, 2)]
        random.shuffle(pairs)
        for i in range(1, grid_size):
            pair = pairs[i-1]
            db.execute(
                "UPDATE squares SET name = ? WHERE pool_id = ? AND x = 0 AND y = ?",
                (f"{pair[0]} and {pair[1]}", pool_id, i)
            )
            db.execute(
                "UPDATE squares SET name = ? WHERE pool_id = ? AND x = ? AND y = 0",
                (f"{pair[0]} and {pair[1]}", pool_id, i)
            )

    db.commit()
    return redirect(url_for('view_pool', pool_id=pool_id))

@app.route('/pool/<int:pool_id>')
def view_pool(pool_id):
    pool = get_pool(pool_id)
    if pool is None:
        flash("Pool not found.")
        return redirect(url_for('index'))
    
    pool['squares'] = get_squares(pool_id)  # Add squares to the pool data
    return render_template('view_pool.html', pool=pool)

@app.route('/claim_square/<int:pool_id>/<int:x>/<int:y>', methods=['POST'])
def claim_square_route(pool_id, x, y):
    user_id = session.get('user_id')  # Replace with the logged-in user's ID
    if user_id:
        name = request.form['name']
        claim_square(pool_id, x, y, name)
        return redirect(url_for('view_pool', pool_id=pool_id))
    return redirect(url_for('auth.login'))

@app.route('/delete_pool/<int:pool_id>', methods=['POST'])
def delete_pool_route(pool_id):
    delete_pool(pool_id)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)