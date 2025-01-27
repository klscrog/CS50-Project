from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
import sqlite3
from authorization_helper import auth_bp, login_required
from database_helper import get_db, get_pool, get_pools, claim_square, delete_pool, user_pools
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ensure you have a secret key for session management

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

@app.route('/new_session')
def new_session():
    return render_template('new_session.html')

# log in
@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# log out
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# get specific pool
@app.route('/pool/<int:pool_id>')
def view_pool(pool_id):
    pool = get_pool(pool_id)
    return render_template('pool.html', pool=pool)

# get all pools
@app.route('/pools')
def list_pools():
    pools = get_pools()
    return render_template('pools.html', pools=pools)

# claim square
@app.route('/claim_square/<int:pool_id>/<int:x>/<int:y>', methods=['POST'])
def claim_square_route(pool_id, x, y):
    user_id = session.get('user_id')  # Replace with the logged-in user's ID
    if user_id:
        claim_square(pool_id, x, y, user_id)
        return redirect(url_for('view_pool', pool_id=pool_id))
    return redirect(url_for('auth.login'))

# delete pool
@app.route('/delete_pool/<int:pool_id>', methods=['POST'])
def delete_pool_route(pool_id):
    delete_pool(pool_id)
    return redirect(url_for('list_pools'))

if __name__ == '__main__':
    app.run(debug=True)