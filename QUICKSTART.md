# Quick Start Guide

## One-Click Start (Windows)

Simply double-click `start.bat` to launch all components automatically!

The script will:
1. Install Python dependencies
2. Start Backend Server (port 5000)
3. Start Admin Console (port 5001)
4. Start User Wallet (port 8080)
5. Start Gate Reader (port 8081)
6. Open Admin Console in your browser

Press any key when prompted to stop all services.

## Manual Start

### Terminal 1 - Backend Server
```powershell
cd backend
python app.py
```

### Terminal 2 - Admin Console
```powershell
cd backend
python admin_console.py
```

### Terminal 3 - User Wallet
```powershell
cd user-wallet-app
python -m http.server 8080
```

### Terminal 4 - Gate Reader
```powershell
cd gate-reader-app
python -m http.server 8081
```

## First-Time Setup

### 1. Register a Gate
- Open Admin Console: http://localhost:5001
- Go to "Register Gate" tab
- Enter:
  - Tablet ID: `GATE001`
  - GPS Location: `22.3193,114.1694`
  - Site: `Main Campus`
- Click "Register Gate"

### 2. Test User Flow
- Open User Wallet: http://localhost:8080
- Login with:
  - iAmSmart ID: `USER001`
  - Password: `demo123`
- Apply for a pass:
  - Site: Main Campus
  - Purpose: Meeting
  - Date: Today + 1 hour
- Submit application

### 3. Approve Pass
- Go to Admin Console: http://localhost:5001
- Click "Pending Passes" tab
- Click "✓ Approve" on the pending pass

### 4. Test Gate Flow
- Open Gate Reader: http://localhost:8081
- Login with:
  - Tablet ID: `GATE001`
  - Password: `demo123`
- Click "Start Scanning"
- Allow camera access
- On User Wallet, go to "My Passes"
- Tap the approved pass (green card)
- Show QR code to gate reader camera
- See "ACCESS GRANTED" result

## Test Credentials

**Users**: Any ID starting with "USER" (e.g., USER001, USER002)
**Password**: `demo123`

**Gates**: `GATE001` (must register first)
**Password**: `demo123`

## URLs
- Backend API: http://localhost:5000
- Admin Console: http://localhost:5001
- User Wallet: http://localhost:8080
- Gate Reader: http://localhost:8081

## Troubleshooting

**Port already in use?**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000
# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Camera not working?**
- Use Chrome or Edge browser
- Grant camera permissions when prompted
- Ensure good lighting
- Try localhost instead of 127.0.0.1

**QR not scanning?**
- Regenerate QR if expired (60s limit)
- Hold phone steady in scan frame
- Increase brightness
- Ensure QR is not too small

## Features to Test

✅ **User Features**:
- Login with iAmSmart ID
- Apply for multiple passes
- View application status
- Generate time-limited QR codes
- View pass history

✅ **Gate Features**:
- Login with tablet ID
- Scan QR codes
- Validate passes
- View access results

✅ **Admin Features**:
- View dashboard statistics
- Approve/reject pass applications
- Revoke active passes
- Pause entire system
- Pause specific sites
- View audit logs
- Register new gates

✅ **Security Features**:
- Digital signature verification
- Single-use pass enforcement
- Time-limited QR codes
- Audit logging
- System pause controls

## Debug Mode

All apps show debug console at bottom with real-time logs.
Check for detailed operation info, errors, and API calls.
