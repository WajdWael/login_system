from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Needed for session & flash messages

# Database setup (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- Database Model ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Create all tables (if they don't exist)
with app.app_context():
    db.create_all()

# ---------- Role‑based access decorator ----------
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
    """Home page – redirects to login or dashboard if already logged in."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Choose another.', 'danger')
            return redirect(url_for('register'))

        # Create new user (role defaults to 'user')
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page – authenticates user and starts a session."""
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Store user id and role in session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Normal user dashboard – accessible by any logged‑in user."""
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], role=session['role'])

@app.route('/admin')
@role_required('admin')
def admin_panel():
    """Admin only page – shows list of all users."""
    all_users = User.query.all()
    return render_template('admin.html', users=all_users)

@app.route('/logout')
def logout():
    """Logs out the user – clears the session."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ---------- Create an admin user ----------
def create_admin_if_needed():
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            # You can change these credentials
            admin_user = User(username='admin')
            admin_user.set_password('admin123')
            admin_user.role = 'admin'
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username 'admin', password 'admin123'")

create_admin_if_needed()

if __name__ == '__main__':
    app.run(debug=True)