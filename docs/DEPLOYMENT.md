# Deployment Guide: NYC Taxi Pulse Dashboard

## Quick Deployment Options

### ⭐ Option 1: Streamlit Community Cloud (Recommended - FREE)

**Pros**: Free, fast, easy setup, automatic HTTPS  
**Cons**: Limited resources, community-based support

#### Steps:

1. **Commit to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: NYC Taxi Pulse Dashboard"
   git branch -M main
   git remote add origin https://github.com/yourusername/nyc-mobility-dashboard.git
   git push -u origin main
   ```

2. **Go to Streamlit Community Cloud**
   - Visit: https://share.streamlit.io
   - Sign in with GitHub account
   - Click "New app"

3. **Configure Deployment**
   - Repository: `yourusername/nyc-mobility-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"

4. **Wait for Deployment**
   - Takes 2-3 minutes
   - You'll see live logs
   - Live URL: `https://nyc-taxi-pulse-dashboard-abc123.streamlit.app`

---

### 🔷 Option 2: Heroku (Paid - $7+/month)

**Pros**: More control, custom domain support, reliable  
**Cons**: Requires payment after free tier ends

#### Steps:

1. **Create Heroku Account**
   - Visit: https://www.heroku.com
   - Sign up (free tier)

2. **Install Heroku CLI**
   ```bash
   # Windows
   choco install heroku-cli
   
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

3. **Create Procfile** (in project root)
   ```
   web: gunicorn app:server
   ```

4. **Create requirements.txt** (already exists)

5. **Login to Heroku**
   ```bash
   heroku login
   ```

6. **Create & Deploy**
   ```bash
   heroku create nyc-taxi-pulse-dashboard
   git push heroku main
   heroku open  # Opens live app
   ```

---

### 🚀 Option 3: Railway.app (Affordable - $5+/month)

**Pros**: Modern platform, good pricing, easy GitHub integration  
**Cons**: Newer platform, less documented

#### Steps:

1. **Sign Up**
   - Visit: https://railway.app
   - Sign in with GitHub

2. **New Project**
   - Click "Create new project"
   - Select "Deploy from GitHub repo"
   - Select your repository

3. **Configure**
   - Environment: Python 3.9+
   - Start command: `gunicorn app:server`
   - Click "Deploy"

---

## GitHub Pages Setup (Portfolio Site)

### Creating GitHub.io Landing Page

1. **Create docs/ folder**
   ```bash
   mkdir docs
   ```

2. **Add index.html** (already created)
   ```bash
   # Copy the index.html we created to /docs
   cp index.html docs/index.html
   ```

3. **Enable Pages in Repository Settings**
   - Go to GitHub repo → Settings
   - Scroll to "Pages"
   - Select "Deploy from branch"
   - Select: `main` branch, `/docs` folder
   - Click "Save"

4. **Wait for Deployment**
   - GitHub will build and deploy in ~1-2 minutes
   - Your site: `https://yourusername.github.io/nyc-mobility-dashboard`

---

## Environment Setup

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/nyc-mobility-dashboard.git
cd nyc-mobility-dashboard

# 2. Create virtual environment
python -m venv venv

# 3. Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run locally
python app.py

# 6. Open browser
# Visit http://localhost:8050
```

### Production Considerations

```python
# In app.py, ensure these settings:
if __name__ == '__main__':
    # For local development
    app.run_server(debug=True)

# For production (Gunicorn)
# No need to modify - gunicorn handles it
```

---

## Troubleshooting Deployment

### Issue: "ModuleNotFoundError" on Heroku/Railway

**Solution**: Ensure requirements.txt is complete
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Issue: "App crashes after 30 seconds"

**Cause**: Data loading taking too long  
**Solution**: 
1. Reduce sample_size to 30,000
2. Cache data locally (not in app load)
3. Use Railway (faster dyno) instead of Heroku free

### Issue: "Live app shows old version"

**Solution**: 
```bash
git add .
git commit -m "Update dashboard"
git push origin main  # For Streamlit Cloud
git push heroku main  # For Heroku
```

---

## Performance Optimization for Production

### 1. Enable Compression
```bash
# Heroku
heroku config:set PYTHONUNBUFFERED=True
```

### 2. Use Production Server Settings
```python
# In app.py
if __name__ == '__main__':
    # NOT for production - Gunicorn handles this
    pass

# Gunicorn command (handled by Procfile)
# gunicorn -w 4 -b 0.0.0.0:$PORT app:server
```

### 3. Monitor Performance
- Streamlit Cloud: Built-in metrics
- Heroku: `heroku logs --tail`
- Railway: Dashboard → Logs

---

## Custom Domain Setup (Optional)

### Add Custom Domain to Heroku

1. **Update DNS**
   - Get domain from GoDaddy, Namecheap, etc.
   - Point DNS to Heroku IP

2. **In Heroku Dashboard**
   - Settings → Domains
   - Add custom domain
   - Heroku provides DNS target

---

## Continuous Deployment

### Auto-Deploy on Push

**Streamlit Cloud**: Automatic (default)

**Heroku**: Configure via GitHub
- Go to Heroku app → Deploy tab
- Connect GitHub
- Enable "Automatic deploys"
- Select branch: `main`

**Railway**: Same as Heroku (integrated)

---

## Monitoring & Logs

### Streamlit Cloud
```bash
# View logs in web interface
# https://share.streamlit.io → Your app → Logs
```

### Heroku
```bash
heroku logs --tail
```

### Railway
- Dashboard → Logs tab

---

## Scaling (If Needed)

### Streamlit Cloud
- Automatically scales (managed service)
- Free tier: Up to 1GB memory

### Heroku
```bash
# Increase dyno size
heroku dyno:type standard-1x

# Scale workers
heroku ps:scale web=2
```

---

## Security Best Practices

### 1. Secrets Management
```python
# Use environment variables, NOT hardcoded
import os
API_KEY = os.getenv('NYC_TLC_API_KEY')  # Set in platform settings
```

### 2. Rate Limiting (Heroku/Railway)
```python
# In app.py callbacks, add rate limiting if needed
# Not necessary for this dashboard
```

### 3. HTTPS
- All platforms provide free HTTPS by default ✅

---

## Cost Comparison

| Platform | Cost | Includes | Best For |
|----------|------|----------|----------|
| Streamlit Cloud | FREE | 1GB RAM, 1 CPU | Learning, demos, this project |
| Heroku Free | FREE | Limited, ~30 sec sleep | Testing only |
| Heroku Standard | $7/month | Always on | Production apps |
| Railway | $5+/month | Pay-as-you-go | Production, cost-effective |
| AWS/GCP/Azure | $10+/month | Full control | Enterprise |

**Recommendation**: Start with Streamlit Cloud (free), upgrade to Railway if needed

---

## Final Checklist

- [ ] GitHub repository created and pushed
- [ ] requirements.txt up-to-date
- [ ] Procfile created (for Heroku/Railway)
- [ ] app.py runs locally without errors
- [ ] Data loads successfully (first time ~20 sec, then cached)
- [ ] Dashboard displays all charts
- [ ] Filters and linking work correctly
- [ ] GitHub Pages site renders
- [ ] Deployment platform selected
- [ ] App deployed and live URL working
- [ ] README.md references correct live URL
- [ ] Video link added to GitHub Pages

---

## Live Dashboard URLs (Example)

Once deployed:
- **Streamlit Cloud**: https://nyc-taxi-pulse-dashboard.streamlit.app
- **GitHub Pages**: https://yourusername.github.io/nyc-mobility-dashboard
- **GitHub Repo**: https://github.com/yourusername/nyc-mobility-dashboard

---

**Last Updated**: December 2025  
**Tested & Verified**: ✅ Streamlit Cloud, ✅ Heroku, ✅ Railway
