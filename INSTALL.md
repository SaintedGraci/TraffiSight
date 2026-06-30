# TraffiSight AI - Installation Guide

## Quick Installation (Recommended)

### Step 1: Install Prerequisites

Download and install these (if not already installed):

1. XAMPP (includes PHP and MySQL)
   - Download: https://www.apachefriends.org/
   - Install with default settings

2. Node.js
   - Download: https://nodejs.org/ (choose LTS version)
   - Install with default settings

### Step 2: Start MySQL

1. Open XAMPP Control Panel
2. Click "Start" next to MySQL
3. Wait for green "Running" status

### Step 3: Run Automatic Installer

1. Double-click: EASY_INSTALL.bat
2. Follow the prompts (installer handles everything automatically)
3. Wait 10-20 minutes for completion
4. If Python is not installed, the installer will download it automatically

### Step 4: Database Setup

When prompted by the installer:

1. Type 'y' to edit .env file
2. Update database password if you set one:
   ```
   DB_PASSWORD=your_mysql_password
   ```
3. Save and close
4. Type 'y' to run database migrations

### Step 5: Launch Application

1. Double-click: start.bat
2. Browser opens at http://localhost:8000
3. Login with:
   - Email: admin@traffisight.com
   - Password: admin123

Done! You can now upload and analyze traffic videos.

## Manual Installation

If automatic installation fails, follow these steps:

### 1. Install PHP Dependencies
```bash
composer install
```

### 2. Install Node.js Dependencies
```bash
npm install
npm run build
```

### 3. Setup Environment
```bash
copy .env.example .env
php artisan key:generate
php artisan storage:link
```

### 4. Configure Database

Edit .env file:
```
DB_DATABASE=traffisight
DB_USERNAME=root
DB_PASSWORD=your_password
```

Create database in MySQL:
```sql
CREATE DATABASE traffisight;
```

Run migrations:
```bash
php artisan migrate --seed
```

### 5. Install Python Dependencies
```bash
cd python_ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
cd ..
```

### 6. Download AI Model

Download yolov8n.pt from:
https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

Save to: python_ai/models/yolov8n.pt

### 7. Start Application
```bash
php artisan serve
```

Visit http://localhost:8000

## Daily Usage

To start the application after installation:

1. Open XAMPP Control Panel
2. Start MySQL (if not running)
3. Double-click: start.bat
4. Login and use normally

To stop:
- Close the command window

## Troubleshooting

### Problem: Python not found
Solution: Run EASY_INSTALL.bat - it will download Python automatically

### Problem: PHP not found
Solution: Install XAMPP first, then run EASY_INSTALL.bat again

### Problem: Database connection error
Solution:
1. Make sure MySQL is running in XAMPP
2. Create database named 'traffisight' in phpMyAdmin
3. Check .env file has correct database credentials
4. Run: php artisan migrate --seed

### Problem: Port 8000 already in use
Solution: Edit start.bat and change to different port:
```
php artisan serve --port=8001
```

### Problem: AI detection not working
Solution:
1. Check python_ai/models/yolov8n.pt exists
2. Run: cd python_ai && venv\Scripts\activate && pip install -r requirements.txt

### Problem: Storage permission errors
Solution:
```bash
php artisan storage:link
```

## System Requirements

Minimum:
- Windows 10 or higher
- 4GB RAM
- 10GB free disk space
- Internet connection (for installation)

Recommended:
- 8GB RAM or higher
- 20GB free disk space
- SSD for faster processing

## Support Files

- README.md - System overview and features
- API_DOCUMENTATION.md - Technical reference for developers
- python_ai/README.md - Python AI engine details

## Installation Files

- EASY_INSTALL.bat - Automatic installer (recommended)
- install.bat - Advanced installer
- setup-python-dependencies.bat - Python-only installer
- start.bat - Application launcher
