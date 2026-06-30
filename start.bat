@echo off
echo.
echo ===================================
echo   TraffiSight AI - Starting...
echo ===================================
echo.

REM Start Laravel development server
echo Starting web application...
start cmd /k "php artisan serve"

echo.
echo Application started at http://localhost:8000
echo.
echo Login credentials:
echo   Email: admin@traffisight.com
echo   Password: admin123
echo.
echo Press any key to open browser...
pause >nul

REM Open browser
start http://localhost:8000

echo.
echo TraffiSight AI is now running!
echo Close the command window to stop the server.
echo.
