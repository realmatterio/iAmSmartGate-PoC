# iAmSmartGate System (PoC)

## Quantum-Secure Public Access Control with Hong Kong iAM Smart eID

A functional mock-up demo of a secure access control system using Hong Kong's iAmSmart eID, featuring:
- User Wallet Web App for pass applications and QR code generation
- Access Gate QR Code Reader Web App for verification
- Backend Access Control Server with admin console

## Project Structure

```
iAmSmartGate-PoC/
├── backend/                    # Python Flask backend server
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── models.py              # Database models
│   ├── api_routes.py          # API endpoints
│   ├── admin_routes.py        # Admin API endpoints
│   ├── admin_console.py       # Web-based admin console
│   ├── crypto_utils.py        # Cryptography and HSM functions
│   ├── dummy_integrations.py  # Dummy iAmSmart & GPS validation
│   ├── background_jobs.py     # Background tasks
│   └── requirements.txt       # Python dependencies
├── user-wallet-app/           # User mobile web app
│   └── index.html            # Single-page application
└── gate-reader-app/           # Gate reader web app
    └── index.html            # Single-page application
```

## Features

### Backend Access Control Server
- **User & Gate Management**: Create and manage user/gate accounts with key pairs
- **Pass Application & Approval**: Manual approval workflow via admin console
- **Digital Signatures**: QR codes signed with user's private key (server-side)
- **Atomic Validation**: Single-use enforcement with database transactions
- **Admin Console**: Web UI for approvals, revocations, system/site pause controls
- **Background Jobs**: Automatic pass expiration and audit log cleanup
- **Debug Mode**: Comprehensive logging for all operations

### User Wallet Web App
- **iAmSmart Authentication**: Login with iAmSmart ID (dummy integration)
- **Pass Application**: Form to apply for site visit passes
- **Status Tracking**: View application status (In Process/Pass/No Pass)
- **Dynamic QR Codes**: Time-limited (60s) digitally signed QR codes
- **Pass Management**: View all passes (active/inactive/revoked)
- **Debug Console**: Real-time operation logging

### Access Gate QR Code Reader Web App
- **Gate Authentication**: Tablet login with GPS validation
- **QR Code Scanning**: Camera-based QR code detection
- **Signature Verification**: Validate digital signatures
- **Access Control**: Real-time pass validation with backend
- **Result Display**: Clear Pass/No Pass/Revoked indicators
- **Debug Console**: Scan operation logging

## System Requirements

- **Backend**: Python 3.8+, pip
- **Frontend**: Modern web browser (Chrome, Firefox, Edge, Safari)
- **Camera**: For QR code scanning on gate devices
- **Network**: All components must be on same network or have internet connectivity

## Installation & Setup

### 1. Backend Server Setup

```powershell
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run main API server (port 5000)
python app.py

# In a separate terminal, run admin console (port 5001)
python admin_console.py
```

The backend will:
- Create SQLite database (`iamsmartgate.db`)
- Initialize system state
- Start background jobs
- Listen on `http://localhost:5000` (API) and `http://localhost:5001` (Admin Console)

### 2. User Wallet App Setup

```powershell
# Navigate to user-wallet-app directory
cd user-wallet-app

# Serve with Python HTTP server
python -m http.server 8080
```

Access at: `http://localhost:8080`

### 3. Gate Reader App Setup

```powershell
# Navigate to gate-reader-app directory
cd gate-reader-app

# Serve with Python HTTP server
python -m http.server 8081
```

Access at: `http://localhost:8081`

## Demo Usage

### Initial Setup

1. **Start Backend Server**:
   ```powershell
   cd backend
   python app.py
   ```

2. **Start Admin Console**:
   ```powershell
   cd backend
   python admin_console.py
   ```
   Access at: http://localhost:5001

3. **Register a Gate** (via Admin Console):
   - Go to "Register Gate" tab
   - Tablet ID: `GATE001`
   - GPS Location: `22.3193,114.1694`
   - Site: `Main Campus`
   - Click "Register Gate"

### User Flow

1. **Open User Wallet** (`http://localhost:8080`)
2. **Login**:
   - iAmSmart ID: `USER001` (or any ID starting with "USER")
   - Password: `demo123`
3. **Apply for Pass**:
   - Select site, purpose, and visit date/time
   - Submit application
4. **Admin Approves Pass** (via Admin Console at http://localhost:5001):
   - Go to "Pending Passes" tab
   - Click "✓ Approve" on the pass
5. **View Pass** (User Wallet):
   - Go to "My Passes"
   - Tap on approved pass (green card)
6. **Show QR Code**:
   - QR code displays with 60-second countdown
   - Keep this screen open for gate scanning

### Gate Flow

1. **Open Gate Reader** (`http://localhost:8081`)
2. **Login**:
   - Tablet ID: `GATE001`
   - Password: `demo123`
   - GPS auto-detects (or uses default)
3. **Start Scanning**:
   - Click "📷 Start Scanning"
   - Allow camera access
4. **Scan QR Code**:
   - Point camera at user's QR code
   - System automatically detects and validates
5. **View Result**:
   - ✅ ACCESS GRANTED (green)
   - ❌ ACCESS DENIED (red)
   - ⚠️ PASS REVOKED (yellow)

### Admin Operations

**Access Admin Console**: http://localhost:5001

- **Dashboard**: View system statistics and site-specific metrics
- **Pending Passes**: Approve or reject applications
- **All Passes**: View all passes, revoke active passes
- **Audit Logs**: View all system events
- **System Control**: 
  - Pause/resume entire system
  - Pause/resume specific sites
- **Register Gate**: Add new access gates

## Test Credentials

### Users
- Any iAmSmart ID starting with "USER" (e.g., `USER001`, `USER002`)
- Password: `demo123`

### Gates
- Tablet ID: `GATE001` (must be pre-registered)
- Password: `demo123`
- GPS: Auto-detected or `22.3193,114.1694`

## Sites & Purposes

### Available Sites
- `SITE001`: Main Campus
- `SITE002`: Student Halls
- `SITE003`: Research Center
- `SITE004`: Library

### Available Purposes
- `PURP001`: Meeting
- `PURP002`: Tour
- `PURP003`: Delivery
- `PURP004`: Maintenance

## Security Features

### Implemented
- ✅ Digital signatures on QR codes (RSA-2048)
- ✅ Server-side private key storage (dummy HSM)
- ✅ JWT token-based authentication
- ✅ TLS 1.3 for all communications (HTTPS)
- ✅ Single-use pass enforcement (atomic DB transactions)
- ✅ Time-limited QR codes (60 seconds)
- ✅ Signature verification before access grant
- ✅ Comprehensive audit logging

### Demo Limitations
- ⚠️ **No post-quantum cryptography** (vulnerable to future quantum attacks)
- ⚠️ **GPS spoofing possible** (browser geolocation not secure)
- ⚠️ **Dummy HSM** (in-memory/file storage, not hardware-backed)
- ⚠️ **Dummy iAmSmart integration** (accepts test credentials)

## Configuration

Edit `backend/config.py` for:
- Database path
- JWT secret keys
- QR expiration time (default: 60s)
- Pass expiration check interval (default: 5min)
- Debug mode toggle
- Site/purpose definitions

## Troubleshooting

### Backend won't start
```powershell
# Check Python version
python --version  # Should be 3.8+

# Install dependencies again
pip install -r requirements.txt --upgrade
```

### Camera not working (Gate Reader)
- Ensure HTTPS or localhost (camera requires secure context)
- Grant browser camera permissions
- Try different browser (Chrome recommended)

### QR code not scanning
- Ensure good lighting
- Hold phone steady within scan frame
- QR code must be valid (not expired)
- Try regenerating QR code

### CORS errors
- Ensure all apps use localhost (not 127.0.0.1 or IP)
- Backend has CORS enabled for all origins (demo only)

## Debug Mode

All apps include debug panels showing:
- API calls and responses
- QR generation/scanning events
- Authentication flows
- Error messages

Enable by default. To disable, set `DEBUG_MODE = false` in HTML files.

## Database Schema

SQLite database with tables:
- **users**: iAmSmart ID, public/private key refs, device ID
- **gates**: Tablet ID, GPS, site, public/private key refs
- **passes**: Pass details, status, timestamps, flags
- **audit_logs**: All system events with timestamps
- **system_state**: Global/site pause flags

## API Endpoints

### User APIs (`/api`)
- `POST /login` - User authentication
- `POST /gate-login` - Gate authentication
- `POST /apply-pass` - Apply for pass
- `GET /my-passes` - Get user's passes
- `GET /get-qr/<pass_id>` - Generate QR code
- `POST /scan-qr` - Validate QR code
- `GET /user-info` - Get user info
- `GET /sites` - Get available sites
- `GET /purposes` - Get available purposes

### Admin APIs (`/admin`)
- `GET /pending-passes` - Get pending applications
- `GET /all-passes` - Get all passes (with filters)
- `POST /approve-pass/<pass_id>` - Approve pass
- `POST /reject-pass/<pass_id>` - Reject pass
- `POST /revoke-pass/<pass_id>` - Revoke pass
- `POST /pause-system` - Pause/resume system
- `POST /pause-site` - Pause/resume site
- `GET /system-status` - Get system status
- `GET /statistics` - Get system statistics
- `GET /audit-logs` - Get audit logs
- `POST /register-gate` - Register new gate

## License

Demo/PoC project for educational purposes.

## Support

For issues or questions, check the debug logs in:
- Backend: `backend/server.log`
- User App: Browser console + debug panel
- Gate App: Browser console + debug panel
