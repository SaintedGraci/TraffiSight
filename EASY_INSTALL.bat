@echo off
title TraffiSight AI - Easy Installer
color 0A

:MENU
cls
echo.
echo  ========================================================
echo              TraffiSight AI - Easy Installer
echo  ========================================================
echo.
echo  This installer will automatically:
echo    - Check if Python is installed
echo    - Install Python if needed
echo    - Install all dependencies
echo    - Download AI model
echo    - Setup database
echo    - Start the application
echo.
echo  ========================================================
echo.
echo  Press any key to start installation...
pause >nul

:CHECK_PYTHON
cls
echo.
echo [Step 1/8] Checking Python installation...
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found!
    echo.
    echo Downloading Python installer...
    echo.
    
    REM Download Python installer
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python_installer.exe'}"
    
    if exist python_installer.exe (
        echo.
        echo Installing Python... (Please wait, this may take a few minutes)
        echo IMPORTANT: Make sure to check 'Add Python to PATH' during installation!
        echo.
        pause
        start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
        del python_installer.exe
        echo.
        echo Python installed! Please RESTART this installer.
        pause
        exit
    ) else (
        echo ERROR: Could not download Python installer.
        echo Please install Python manually from python.org
        pause
        exit /b 1
    )
) else (
    python --version
    echo Python is installed!
)
timeout /t 2 >nul

:CHECK_PHP
cls
echo.
echo [Step 2/8] Checking PHP installation...
echo.
php --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: PHP not found!
    echo.
    echo Please install one of these:
    echo   - XAMPP: https://www.apachefriends.org/
    echo   - Laragon: https://laragon.org/download/
    echo   - WAMP: https://www.wampserver.com/
    echo.
    pause
    exit /b 1
) else (
    php --version | findstr /C:"PHP"
    echo PHP is installed!
)
timeout /t 2 >nul

:CHECK_COMPOSER
cls
echo.
echo [Step 3/8] Checking Composer...
echo.
composer --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Composer not found!
    echo.
    echo Downloading Composer...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://getcomposer.org/Composer-Setup.exe' -OutFile 'composer_installer.exe'}"
    
    if exist composer_installer.exe (
        echo Installing Composer...
        start /wait composer_installer.exe
        del composer_installer.exe
        echo.
        echo Composer installed! Please RESTART this installer.
        pause
        exit
    )
) else (
    composer --version | findstr /C:"Composer"
    echo Composer is installed!
)
timeout /t 2 >nul

:CHECK_NODE
cls
echo.
echo [Step 4/8] Checking Node.js...
echo.
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js not found!
    echo.
    echo Opening Node.js download page...
    echo Please download and install Node.js, then restart this installer.
    start https://nodejs.org/
    pause
    exit /b 1
) else (
    node --version
    echo Node.js is installed!
)
timeout /t 2 >nul

:INSTALL_PHP_DEPS
cls
echo.
echo [Step 5/8] Installing PHP dependencies...
echo This may take a few minutes...
echo.
call composer install --no-interaction
if errorlevel 1 (
    echo ERROR: Failed to install PHP dependencies
    pause
    exit /b 1
)
echo PHP dependencies installed!
timeout /t 2 >nul

:INSTALL_NODE_DEPS
cls
echo.
echo [Step 6/8] Installing Node.js dependencies and building assets...
echo This may take a few minutes...
echo.
call npm install --silent
call npm run build
if errorlevel 1 (
    echo ERROR: Failed to install Node dependencies
    pause
    exit /b 1
)
echo Node.js dependencies installed!
timeout /t 2 >nul

:SETUP_ENV
cls
echo.
echo [Step 7/8] Setting up environment...
echo.
if not exist .env (
    copy .env.example .env >nul
    echo .env file created
)
php artisan key:generate
php artisan storage:link
echo Environment setup complete!
timeout /t 2 >nul

:INSTALL_PYTHON_DEPS
cls
echo.
echo [Step 8/8] Installing Python AI dependencies...
echo This is the longest step - may take 5-15 minutes...
echo Please be patient, do not close this window!
echo.

cd python_ai

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        cd ..
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo Installing Python packages (this will take a while)...
echo Progress: Installing opencv-python...
pip install opencv-python==4.9.0.80 --quiet
echo Progress: Installing torch (this is large, please wait)...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
echo Progress: Installing ultralytics...
pip install ultralytics --quiet
echo Progress: Installing remaining packages...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed to install
    echo The system may still work, but AI features might be limited
    pause
)

if not exist .env (
    copy .env.example .env >nul
)

cd ..
echo.
echo Python dependencies installed!
timeout /t 2 >nul

:DOWNLOAD_MODEL
cls
echo.
echo [Bonus Step] Downloading AI Model...
echo.
if not exist python_ai\models\yolov8n.pt (
    echo Downloading YOLOv8 model (6MB)...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt' -OutFile 'python_ai\models\yolov8n.pt'}"
    
    if exist python_ai\models\yolov8n.pt (
        echo AI Model downloaded successfully!
    ) else (
        echo Could not download model automatically.
        echo Please download manually from:
        echo https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
        echo And save to: python_ai\models\yolov8n.pt
    )
) else (
    echo AI Model already exists!
)
timeout /t 2 >nul

:DATABASE_SETUP
cls
echo.
echo [Database Setup]
echo.
echo Before continuing, please ensure:
echo   1. MySQL is running
echo   2. You have created a database named 'traffisight'
echo   3. You have updated .env file with your database credentials
echo.
echo Open .env file now to edit database settings? (y/n)
set /p editenv=
if /i "%editenv%"=="y" (
    notepad .env
    echo.
    echo Press any key after saving .env file...
    pause >nul
)

echo.
echo Run database migrations now? (y/n)
set /p runmigrate=
if /i "%runmigrate%"=="y" (
    php artisan migrate --seed
    if errorlevel 1 (
        echo.
        echo Database migration failed!
        echo Please check your database settings in .env file
        echo.
        pause
        exit /b 1
    )
    echo Database setup complete!
)

:COMPLETE
cls
echo.
echo  ========================================================
echo              Installation Complete!
echo  ========================================================
echo.
echo  Everything is ready to use!
echo.
echo  To start TraffiSight AI:
echo    1. Run: start.bat
echo    2. Open browser: http://localhost:8000
echo    3. Login with:
echo       Email: admin@traffisight.com
echo       Password: admin123
echo.
echo  ========================================================
echo.
echo  Start the application now? (y/n)
set /p startapp=
if /i "%startapp%"=="y" (
    start cmd /k "php artisan serve"
    timeout /t 3 >nul
    start http://localhost:8000
    echo.
    echo Application started!
    echo Browser should open automatically.
)

echo.
echo  Installation log saved to: installation.log
echo  Press any key to exit...
pause >nul
exit
