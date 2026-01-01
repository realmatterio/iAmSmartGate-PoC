# Deploying iAmSmartGate on Render.com - Step-by-Step Guide

## Prerequisites ✅
- [x] Render.com free account created
- [x] GitHub account linked to Render
- [x] Project pushed to GitHub repo

---

## Step 1: Prepare Your GitHub Repo

### 1.1 Commit the new deployment files:
```bash
cd c:\Users\hipopo\Codes\iAmSmartGate\iAmSmartGate-PoC
git add render.yaml backend/requirements.txt
git commit -m "Add Render.com deployment configuration"
git push origin main
```

### 1.2 Verify files exist in GitHub:
- `render.yaml` (root level)
- `backend/requirements.txt` (updated with gunicorn)

---

## Step 2: Create Web Service on Render.com

### 2.1 Go to Render Dashboard
1. Visit https://dashboard.render.com
2. Click **"New +"** button → Select **"Web Service"**

### 2.2 Connect GitHub Repository
1. Click **"Connect a repository"**
2. Select your GitHub repo: **`iAmSmartGate`**
3. Click **"Connect"**

### 2.3 Configure the Web Service

**Basic Settings:**
- **Name:** `iamsmartgate-backend`
- **Repository:** Your GitHub repo
- **Branch:** `main` (or your default branch)
- **Root Directory:** Leave empty (or `.` if required)

**Build & Start Commands:**
- **Build Command:** `pip install -r backend/requirements.txt`
- **Start Command:** `cd backend && gunicorn app:create_app()`

**Environment:**
- **Runtime:** Python 3
- **Region:** Choose closest to your location

### 2.4 Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value | Note |
|-----|-------|------|
| `DEBUG` | `false` | Production safety |
| `TEST_MODE` | `false` | Use real data |
| `ALLOWED_ORIGINS` | `*` | Allow all CORS origins (change later) |
| `SECRET_KEY` | (generate) | Click "Generate" button |
| `JWT_SECRET_KEY` | (generate) | Click "Generate" button |
| `PYTHON_VERSION` | `3.11.7` | (Optional) Specify version |

**Screenshot of Environment Variables:**
```
DEBUG=false
TEST_MODE=false
ALLOWED_ORIGINS=*
SECRET_KEY=[auto-generated]
JWT_SECRET_KEY=[auto-generated]
```

### 2.5 Instance Type & Pricing
- Select **"Free"** tier (for testing)
- Click **"Create Web Service"**

---

## Step 3: Wait for Deployment

### 3.1 Monitor Build Progress
You'll see logs like:
```
=== Building Docker image
=== Installing build runtime
=== Running build command: pip install -r backend/requirements.txt
...
=== Deploying docker image to Render
=== Service live at https://iamsmartgate-backend.onrender.com
```

### 3.2 Deployment Complete
Once you see:
```
✓ Service live at https://iamsmartgate-backend.onrender.com
```
Your backend is **live!** 🎉

**Your API URL:** `https://iamsmartgate-backend.onrender.com`

---

## Step 4: Test Your Backend

### 4.1 Test Health Endpoint
```bash
curl https://iamsmartgate-backend.onrender.com/health
```

Expected response:
```json
{"status": "ok", "timestamp": "2025-12-31T..."}
```

### 4.2 Test API Endpoints
Example:
```bash
curl https://iamsmartgate-backend.onrender.com/api/status
```

### 4.3 Check Logs
In Render Dashboard:
1. Click your service name
2. Go to **"Logs"** tab
3. View real-time logs

---

## Step 5: Deploy Frontend Apps (Optional)

### 5.1 Deploy to Netlify (Easy)

**For `gate-reader-app`:**
1. Visit https://app.netlify.com
2. Click **"Add new site"** → **"Deploy manually"**
3. Drag & drop the `gate-reader-app` folder
4. Site deployed instantly with HTTPS!
5. Note the URL: `https://your-site-name.netlify.app`

**For `user-wallet-app`:**
- Repeat above process

### 5.2 Update Frontend API URLs
Update your frontend JavaScript to use the Render backend:

In `gate-reader-app/index.html`:
```javascript
const API_BASE = 'https://iamsmartgate-backend.onrender.com';

// Replace all API calls:
fetch(`${API_BASE}/api/status`)
  .then(r => r.json())
  .catch(e => console.error(e));
```

Same for `user-wallet-app/index.html`

---

## Step 6: Fix CORS Issues (If Needed)

### If frontend can't reach backend:

**Option A: Open CORS temporarily (Testing)**
1. Go to Render Dashboard → Your service
2. Click **"Environment"** tab
3. Edit `ALLOWED_ORIGINS`:
   ```
   https://your-netlify-app.netlify.app,https://your-other-app.netlify.app
   ```
4. Click **"Save"** (auto-redeploys)

**Option B: Update backend code**
In `backend/config.py`, change:
```python
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
```

In `backend/app.py`, update CORS:
```python
from flask_cors import CORS
import os

allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
CORS(app, resources={r"/*": {"origins": allowed_origins}})
```

Then commit and push - Render auto-redeploys!

---

## Step 7: Monitor & Maintain

### 7.1 View Logs
Render Dashboard → Your service → **"Logs"** tab

### 7.2 Check Metrics
- **CPU Usage**
- **Memory Usage**
- **Network I/O**
(Free tier has basic monitoring)

### 7.3 Restart Service
Click **"Restart"** if needed (in Render Dashboard)

### 7.4 Enable Auto-Deploy
Render automatically redeploys when you push to GitHub (already enabled)

---

## Troubleshooting

### ❌ Build Fails
Check logs for Python import errors:
1. Go to **"Logs"** tab
2. Look for `ModuleNotFoundError` or `ImportError`
3. Update `backend/requirements.txt` with missing packages
4. Commit and push - Render auto-redeploys

### ❌ CORS Errors
Frontend console shows: `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**
- Update `ALLOWED_ORIGINS` environment variable
- Or temporarily set to `*` for testing

### ❌ Database Issues
If you use PostgreSQL in production:
1. Add to Render: **"PostgreSQL"** service
2. Copy connection string
3. Set `DATABASE_URL` environment variable
4. Current: SQLite (fine for testing, limited for production)

### ❌ Service Keeps Restarting
1. Check logs for memory leaks
2. Free tier has 512MB RAM limit
3. Upgrade to paid if needed

---

## Production Checklist

Before going public:
- [ ] Set `DEBUG=false`
- [ ] Set `TEST_MODE=false`
- [ ] Generate strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Restrict `ALLOWED_ORIGINS` to your domains only
- [ ] Enable HTTPS (automatic on Render)
- [ ] Test all API endpoints
- [ ] Monitor logs regularly
- [ ] Set up error alerts (Render Pro feature)

---

## Your Live URLs

| Service | URL |
|---------|-----|
| Backend API | `https://iamsmartgate-backend.onrender.com` |
| Health Check | `https://iamsmartgate-backend.onrender.com/health` |
| Frontend (if deployed) | `https://your-site.netlify.app` |

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Create Web Service on Render
3. ✅ Wait for deployment
4. ✅ Test with curl or Postman
5. ✅ Deploy frontends to Netlify
6. ✅ Update frontend API URLs
7. ✅ Fix CORS if needed
8. ✅ Monitor logs

**Need help?** Check Render docs: https://render.com/docs

