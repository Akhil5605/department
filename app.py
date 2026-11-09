# app.py
# Complete Flask backend for Department Webpage
# Run: python app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import hashlib
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production-2026'

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'yourpassword',
    'database': 'department_db',
    'autocommit': False,
    'charset': 'utf8mb4',
}


def get_db_connection():
    """Create and return a database connection."""
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Create the base users table if it does not already exist."""
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    except Error as exc:
        print(f"Database init failed: {exc}")
    finally:
        connection.close()


def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email):
    """Basic email validation."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def get_user_by_email(email):
    """Fetch user from database by email."""
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, fullname, email, password_hash FROM users WHERE email = %s",
            (email,),
        )
        return cursor.fetchone()
    finally:
        connection.close()


def create_user(fullname, email, password_hash):
    """Insert new user into database."""
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (fullname, email, password_hash) VALUES (%s, %s, %s)",
            (fullname, email, password_hash),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


# ---------- Routes ----------
@app.route('/')
def home():
    """Home page - shows main landing page."""
    return render_template('index.html')


@app.route('/about')
def about():
    """About page - department information."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration - handles both GET and POST requests."""
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not fullname or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))

        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('register'))

        existing_user = get_user_by_email(email)
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))

        hashed_pw = hash_password(password)
        try:
            create_user(fullname, email, hashed_pw)
            flash(f'Registration successful! Welcome {fullname}. Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as exc:
            flash(f'Registration failed: {exc}', 'danger')
            return redirect(url_for('register'))

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login - handles authentication."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return redirect(url_for('login'))

        user = get_user_by_email(email)

        if user:
            user_id, fullname, user_email, stored_hash = user
            if stored_hash == hash_password(password):
                session['user_id'] = user_id
                session['fullname'] = fullname
                session['email'] = user_email
                session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                flash(f'Welcome back, {fullname}!', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid password. Please try again.', 'danger')
        else:
            flash('No account found with that email.', 'danger')

        return redirect(url_for('login'))

    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Protected dashboard - requires login."""
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT fullname, email, created_at FROM users WHERE id = %s",
            (session['user_id'],),
        )
        user_data = cursor.fetchone()
    finally:
        connection.close()

    return render_template(
        'dashboard.html',
        user={
            'fullname': user_data[0],
            'email': user_data[1],
            'created_at': user_data[2],
        } if user_data else None,
        login_time=session.get('login_time'),
    )


@app.route('/logout')
def logout():
    """Logout - clear session."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))


# ---------- Error Handlers ----------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    flash('Something went wrong. Please try again later.', 'danger')
    return render_template('index.html'), 500


# ---------- Run the App ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)