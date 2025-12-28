@echo off
echo ========================================
echo iAmSmartGate System - Quick Start
echo ========================================
echo.

echo Step 1: Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo Step 2: Starting Backend Server...
start "iAmSmartGate Backend" cmd /k "python app.py"
timeout /t 3 /nobreak >nul
echo ✓ Backend server started on http://localhost:5000
echo.

echo Step 3: Starting Admin Console...
start "iAmSmartGate Admin Console" cmd /k "python admin_console.py"
timeout /t 3 /nobreak >nul
echo ✓ Admin console started on http://localhost:5001
echo.

cd ..

echo Step 4: Starting User Wallet App...
cd user-wallet-app
start "iAmSmartGate User Wallet" cmd /k "python -m http.server 8080"
timeout /t 2 /nobreak >nul
echo ✓ User Wallet started on http://localhost:8080
echo.

cd ..

echo Step 5: Starting Gate Reader App...
cd gate-reader-app
start "iAmSmartGate Gate Reader" cmd /k "python -m http.server 8081"
timeout /t 2 /nobreak >nul
echo ✓ Gate Reader started on http://localhost:8081
echo.

echo ========================================
echo All systems started successfully!
echo ========================================
echo.
echo Access URLs:
echo   Backend API:    http://localhost:5000
echo   Admin Console:  http://localhost:5001
echo   User Wallet:    http://localhost:8080
echo   Gate Reader:    http://localhost:8081
echo.
echo Opening Admin Console in browser...
timeout /t 2 /nobreak >nul
start http://localhost:5001
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping all services...
taskkill /FI "WindowTitle eq iAmSmartGate Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq iAmSmartGate Admin Console*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq iAmSmartGate User Wallet*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq iAmSmartGate Gate Reader*" /T /F >nul 2>&1
echo ✓ All services stopped
echo.
pause
