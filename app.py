from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import logging
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database setup (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- Logging Setup ----------
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# ---------- Account Lockout Settings ----------
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 300  # 5 minutes in seconds

# In-memory store: { username: { 'attempts': int, 'lockout_until': float } }
login_attempts = {}

# ---------- Database Model ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

with app.app_context():
    db.create_all()

# ---------- Role-based access decorator ----------
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if user.role != required_role:
                flash('You do not have permission to view this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ---------- Routes ----------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Choose another.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        logging.info(f"New user registered: {username}")
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        # -------- SQL Injection Detection --------
        sql_keywords = ["'", '"', "--", ";", "OR", "AND", "=", "/*", "*/", "DROP", "SELECT", "INSERT"]
        for keyword in sql_keywords:
            if keyword.lower() in username.lower() or keyword.lower() in password.lower():
                logging.warning(f"SQL Injection attempt detected! Input: username='{username}'")
                flash('Invalid input detected. SQL Injection attempt blocked.', 'danger')
                return render_template('login.html')

        # -------- Account Lockout Check --------
        now = time.time()
        if username in login_attempts:
            user_data = login_attempts[username]
            if user_data.get('lockout_until') and now < user_data['lockout_until']:
                remaining = int(user_data['lockout_until'] - now)
                flash(f'Account is locked. Please try again in {remaining} seconds.', 'danger')
                logging.info(f"Locked account login attempt for username: {username}")
                return render_template('login.html')

        # -------- Authenticate --------
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_attempts.pop(username, None)
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            logging.info(f"Successful login for username: {username}")
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            if username not in login_attempts:
                login_attempts[username] = {'attempts': 0, 'lockout_until': None}

            login_attempts[username]['attempts'] += 1
            attempts = login_attempts[username]['attempts']
            logging.info(f"Failed login attempt {attempts}/{MAX_ATTEMPTS} for username: {username}")

            if attempts >= MAX_ATTEMPTS:
                login_attempts[username]['lockout_until'] = now + LOCKOUT_TIME
                login_attempts[username]['attempts'] = 0
                flash(f'Account locked after {MAX_ATTEMPTS} failed attempts. Try again in 5 minutes.', 'danger')
                logging.info(f"Account LOCKED for username: {username}")
            else:
                remaining_attempts = MAX_ATTEMPTS - attempts
                flash(f'Invalid username or password. {remaining_attempts} attempt(s) remaining before lockout.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], role=session['role'])

@app.route('/admin')
@role_required('admin')
def admin_panel():
    all_users = User.query.all()
    return render_template('admin.html', users=all_users)

@app.route('/logout')
def logout():
    logging.info(f"User logged out: {session.get('username', 'unknown')}")
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ---------- Create admin user if not exists ----------
def create_admin_if_needed():
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin_user = User(username='admin')
            admin_user.set_password('admin123')
            admin_user.role = 'admin'
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username 'admin', password 'admin123'")

create_admin_if_needed()

if __name__ == '__main__':
    app.run(debug=True)
