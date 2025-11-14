# Vercel Deployment Guide

## Step-by-Step Deployment

### Step 1: Install Vercel CLI

**Windows (PowerShell):**
```powershell
npm install -g vercel
```

Or if you don't have Node.js:
```powershell
# Install Node.js first from nodejs.org, then:
npm install -g vercel
```

### Step 2: Login to Vercel

```powershell
vercel login
```

This will open a browser for authentication. Sign in with GitHub, GitLab, or Bitbucket.

### Step 3: Deploy to Vercel

Navigate to your project directory:

```powershell
cd c:\Users\prita\OneDrive\Desktop\flask-analytics
vercel
```

When prompted:
- **Set up and deploy?** → Yes
- **Which scope?** → Select your account
- **Link to existing project?** → No (for first deployment)
- **Project name?** → `flask-analytics` (or your preferred name)
- **Directory?** → `./` (current directory)
- **Override settings?** → No

### Step 4: Set Environment Variables

After deployment, set your environment variables:

**Option A: Via Vercel Dashboard (Recommended)**
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add these variables:

```
REDIS_URL = rediss://default:AT_xAAIncDI3OTc2ZTM0YTNlNTQ0NjE3OGNkNmY0ZWFhYzdiOTdhOXAyMTYzNjk@singular-mako-16369.upstash.io:6379
REDIS_QUEUE_NAME = python-proj
DATABASE_URL = mysql+pymysql://i3f5PA8K9VVwKFa.root:yhEmdbFR8KUgxIAO@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test
FORCE_SSL = false
TIDB_CA_PATH = ./isrgrootx1.pem
```

5. Select **Production**, **Preview**, and **Development** environments
6. Click **Save**

**Option B: Via CLI**
```powershell
vercel env add REDIS_URL
# Paste your Redis URL when prompted

vercel env add REDIS_QUEUE_NAME
# Enter: python-proj

vercel env add DATABASE_URL
# Paste your database URL when prompted

vercel env add FORCE_SSL
# Enter: false

vercel env add TIDB_CA_PATH
# Enter: ./isrgrootx1.pem (or leave empty if not using SSL)
```

### Step 5: Redeploy with Environment Variables

After setting environment variables, redeploy:

```powershell
vercel --prod
```

### Step 6: Get Your App URL

After deployment, Vercel will provide you with:
- **Production URL**: `https://your-project-name.vercel.app`
- **Preview URLs**: For each deployment

### Step 7: Test Your Deployment

1. Visit your Vercel URL in a browser
2. You should see the Analytics Dashboard
3. Try sending a test event
4. Check the `/stats` endpoint

## Important Notes

### Worker Process
- **Vercel doesn't run background workers**
- You'll need to deploy the worker separately on:
  - Fly.io (recommended)
  - Railway
  - Render
  - PythonAnywhere
  - Or any other platform that supports long-running processes

### Database Tables
- Initialize tables before using the app
- Run `create_tables.py` locally or on another service
- Or create tables manually in your database

### SSL Certificate
- If using TiDB with SSL, you'll need to include the certificate file
- For Vercel, you may need to embed the certificate or use a different approach
- Consider using `FORCE_SSL=false` if possible

## Troubleshooting

### Build Fails
- Check `vercel.json` configuration
- Verify `requirements.txt` has all dependencies
- Check build logs in Vercel dashboard

### Connection Errors
- Verify environment variables are set correctly
- Check that Redis/Database allow connections from Vercel IPs
- Verify SSL configuration if using SSL

### Function Timeout
- Vercel has execution time limits (10s on free tier, 60s on Pro)
- For long-running operations, consider using background jobs

## Useful Commands

```powershell
# Deploy to production
vercel --prod

# Deploy to preview
vercel

# View deployment logs
vercel logs

# List all deployments
vercel ls

# Remove deployment
vercel remove
```

## Next Steps

1. Deploy Flask API on Vercel (this guide)
2. Deploy worker separately on Fly.io/Railway/Render
3. Test the complete system
4. Set up monitoring and alerts

