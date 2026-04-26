# Secure Login System with SQL Injection Prevention
A secure web-based login system built with Python Flask and SQLite.

## Features
- Secure login with password hashing (PBKDF2-SHA256)
- SQL Injection detection and prevention
- Account lockout after 3 failed attempts within 5 minutes
- Login attempt logging
- Role-based access control (admin/user)

## Requirements
- Python 3.x
- Flask
- Flask-SQLAlchemy
- Werkzeug

## Installation & Running

### Step 1: Install dependencies
pip install flask flask-sqlalchemy werkzeug

### Step 2: Run the application
python app.py

### Step 3: Open in browser
http://127.0.0.1:5000

## Default Admin Account
- Username: admin
- Password: admin123

## Project Structure
flask_login_system/
├── app.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── admin.html
└── README.md

## Course
CS471 - Computer Security
