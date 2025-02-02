from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database_helper import create_user, get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirmation = request.form['confirmation']

        if not username:
            flash("Please enter username")
            return redirect(url_for('auth.register'))
        if not email:
            flash("Please enter email")
            return redirect(url_for('auth.register'))
        if not password:
            flash("Please enter password")
            return redirect(url_for('auth.register'))
        if not confirmation:
            flash("Please confirm password")
            return redirect(url_for('auth.register'))
        if password != confirmation:
            flash("Password must match confirmation")
            return redirect(url_for('auth.register'))

        # Hash the password
        password_hash = generate_password_hash(password)  

        try:
            create_user(username, email, password_hash)
            db = get_db()
            new_user = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            session["user_id"] = new_user["id"]
        except sqlite3.IntegrityError:
            flash("Username or email already taken")
            return redirect(url_for('auth.register'))

        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials")
            return render_template('login.html')
    return render_template('login.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function