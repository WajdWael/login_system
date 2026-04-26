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

### Step 1: Extract the ZIP file
Extract the downloaded ZIP file to any location on your computer.
- On Windows: Right-click the ZIP file → `Extract All` → Choose your destination folder
- On Mac: Double-click the ZIP file to extract it automatically

> **Note:** The folder location may vary depending on where you extracted the files.
> Make sure to navigate to the correct folder path in the next step.

### Step 2: Open Terminal or Command Prompt

**On Windows:**
1. Press `Windows + R` → type `cmd` → press Enter

**On Mac:**
1. Press `Command + Space` → type `Terminal` → press Enter

### Step 3: Navigate to the project folder
Replace `your/path/to` with the actual path where you extracted the project.

```
cd your/path/to/flask_login_system
```

**Example on Windows (if extracted to Desktop):**
```
cd Desktop/flask_login_system
```

**Example on Mac (if extracted to Downloads):**
```
cd Downloads/flask_login_system
```

> **Note:** If you see `No such file or directory`, it means the path is wrong.
> Open the extracted folder, click on the address bar at the top, 
> and copy the full path from there.

### Step 4: Install dependencies
```
pip install flask flask-sqlalchemy werkzeug
```

> **Note:** This step requires an internet connection.
> If you get a permission error, try: `pip install --user flask flask-sqlalchemy werkzeug`

### Step 5: Run the application
```
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Press CTRL+C to quit
```

> **Note:** Keep this terminal window open while using the application.
> Closing it will stop the server.

### Step 6: Open in your browser
Open any browser and go to:
```
http://127.0.0.1:5000
```

## Default Admin Account
- Username: `admin`
- Password: `admin123`

## Project Structure
```
flask_login_system/
├── app.py              ← Main application file
├── templates/          ← HTML pages
│   ├── base.html       ← Shared layout for all pages
│   ├── login.html      ← Login page
│   ├── register.html   ← Registration page
│   ├── dashboard.html  ← User dashboard
│   └── admin.html      ← Admin panel
└── README.md           ← Project documentation
```

> **Note:** The `instance/` folder (containing the database) and `app.log` (login attempts log)
> will be created automatically when you run the application for the first time.

## Course
CS471 - Computer Security
