# Quick Render.com Deployment Checklist

## Pre-Deployment (Do This Now)

```bash
# 1. Navigate to project
cd c:\Users\hipopo\Codes\iAmSmartGate\iAmSmartGate-PoC

# 2. Check Git status
git status

# 3. Commit new files
git add render.yaml backend/requirements.txt RENDER_DEPLOYMENT.md
git commit -m "Prepare for Render.com deployment"

# 4. Push to GitHub
git push origin main

# 5. Verify on GitHub (open browser)
# Visit your repo and confirm files are there
```

---

## Render.com Deployment (5 minutes)

### Step 1: Create Web Service
```
🌐 Go to: https://dashboard.render.com
📍 Click: "New +" → "Web Service"
🔗 Select: Your GitHub repo
✅ Click: "Connect"
```

### Step 2: Fill Configuration
```
Name:                  iamsmartgate-backend
Repository:            (auto-filled)
Branch:                main
Root Directory:        (leave empty)
Runtime:               Python 3
Region:                Frankfurt (or nearest)

Build Command:         pip install -r backend/requirements.txt
Start Command:         cd backend && gunicorn app:create_app()

Instance Type:         FREE (for testing)
```

### Step 3: Add Environment Variables
```
Click "Advanced" → "Add Environment Variable"

DEBUG                = false
TEST_MODE            = false
ALLOWED_ORIGINS      = *
SECRET_KEY           = [Click "Generate"]
JWT_SECRET_KEY       = [Click "Generate"]
```

### Step 4: Deploy
```
Click "Create Web Service"
⏳ Wait 2-5 minutes for deployment
✅ You'll see: "Service live at https://iamsmartgate-backend.onrender.com"
```

### Step 5: Verify
```bash
# Test in PowerShell
curl https://iamsmartgate-backend.onrender.com/health

# Expected response:
# {"status":"ok","timestamp":"2025-12-31T..."}
```

---

## Your Backend URL
```
https://iamsmartgate-backend.onrender.com
```

Use this URL in your frontend apps!

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Add missing package to `backend/requirements.txt` → Push |
| CORS Error | Set `ALLOWED_ORIGINS=*` temporarily → Push |
| Service won't start | Check logs in Render Dashboard → Fix → Push |
| Database error | SQLite should work, or add PostgreSQL service |
| Free tier limits | Upgrade to paid ($7/month) if needed |

---

## Next: Deploy Frontend

### Option A: Netlify (Easiest)
```
1. Visit https://app.netlify.com
2. Click "Add new site" → "Deploy manually"
3. Drag & drop "gate-reader-app" folder
4. Get your Netlify URL
5. Update JavaScript to use your Render backend URL
```

### Option B: GitHub Pages (Free)
```
Push frontend files to `gh-pages` branch
```

---

## File Changes Made

✅ Created: `render.yaml` - Deployment config
✅ Updated: `backend/requirements.txt` - Added gunicorn
✅ Created: `RENDER_DEPLOYMENT.md` - Full guide
✅ Created: This checklist

All ready to deploy! 🚀
