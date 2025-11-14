# Fly.io Worker Deployment Guide

## Step-by-Step Instructions

### Step 1: Install Fly CLI

**Windows (PowerShell):**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Mac/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

After installation, restart your terminal or run:
```bash
# Windows
$env:Path += ";$env:USERPROFILE\.fly\bin"

# Mac/Linux
export FLYCTL_INSTALL="/home/$USER/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

### Step 2: Login to Fly.io

```bash
fly auth login
```

This will open a browser for authentication.

### Step 3: Initialize Fly App (Worker)

Navigate to your project directory and initialize:

```bash
cd flask-analytics
fly launch --config fly.worker.toml --no-deploy
```

When prompted:
- **App name**: Use the default or choose a unique name (e.g., `flask-analytics-worker-yourname`)
- **Region**: Choose closest to you (e.g., `iad` for US East, `lhr` for London)
- **Postgres/Redis**: Say "No" (you're using external services)

### Step 4: Set Environment Variables (Secrets)

Set your secrets (these are encrypted):

```bash
fly secrets set REDIS_URL="rediss://default:AT_xAAIncDI3OTc2ZTM0YTNlNTQ0NjE3OGNkNmY0ZWFhYzdiOTdhOXAyMTYzNjk@singular-mako-16369.upstash.io:6379"

fly secrets set DATABASE_URL="mysql+pymysql://i3f5PA8K9VVwKFa.root:yhEmdbFR8KUgxIAO@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test"

fly secrets set REDIS_QUEUE_NAME="python-proj"

fly secrets set FORCE_SSL="false"

fly secrets set TIDB_CA_PATH="./isrgrootx1.pem"
```

**Note:** If you have the CA certificate file, you'll need to copy it into the Docker image. See Step 5.

### Step 5: Handle SSL Certificate (If Needed)

If you need the TiDB CA certificate:

1. Create a directory for certificates:
```bash
mkdir -p certs
```

2. Copy your certificate file to `certs/isrgrootx1.pem`

3. Update Dockerfile.worker to copy the certificate:
```dockerfile
# Add this line before CMD
COPY certs/isrgrootx1.pem ./isrgrootx1.pem
```

Or set `TIDB_CA_PATH=""` if not using SSL.

### Step 6: Deploy Worker

```bash
fly deploy --config fly.worker.toml
```

### Step 7: Check Logs

```bash
fly logs --app flask-analytics-worker
```

You should see:
```
Worker started and connected successfully!
```

### Step 8: Verify It's Running

```bash
# Check status
fly status --app flask-analytics-worker

# View logs in real-time
fly logs --app flask-analytics-worker
```

### Step 9: Test Worker

Send a test event to your Flask API, then check logs:
```bash
fly logs --app flask-analytics-worker
```

You should see `Processing: {...}` messages.

## Useful Fly.io Commands

```bash
# View app status
fly status --app flask-analytics-worker

# View logs
fly logs --app flask-analytics-worker

# SSH into the container (for debugging)
fly ssh console --app flask-analytics-worker

# Restart the app
fly apps restart flask-analytics-worker

# View secrets (names only, not values)
fly secrets list --app flask-analytics-worker

# Update a secret
fly secrets set KEY="value" --app flask-analytics-worker

# Remove a secret
fly secrets unset KEY --app flask-analytics-worker

# Scale the app (if needed)
fly scale count 1 --app flask-analytics-worker
```

## Troubleshooting

### Connection Errors

**Redis Connection Error:**
- Verify `REDIS_URL` is correct
- Check if Upstash allows connections from Fly.io IPs
- Verify SSL configuration

**Database Connection Error:**
- Verify `DATABASE_URL` is correct
- Check if TiDB allows connections from Fly.io IPs
- Verify SSL certificate path if using SSL

### View Detailed Logs

```bash
# Real-time logs
fly logs --app flask-analytics-worker

# Last 100 lines
fly logs --app flask-analytics-worker -n 100
```

### Restart Worker

```bash
fly apps restart flask-analytics-worker
```

### Check App Status

```bash
fly status --app flask-analytics-worker
```

## Free Tier Limits

- **3 shared-cpu-1x VMs** (256MB RAM each)
- **3GB persistent volume storage**
- **160GB outbound data transfer**
- Apps sleep after 5 minutes of inactivity (but wake on first request)

For always-on workers, you may need to:
- Use a paid plan, OR
- Set up a cron job to ping the worker periodically

## Cost

- **Free tier**: 3 VMs, perfect for workers
- **Paid**: Starts at ~$2/month per VM for always-on

## Next Steps

1. Deploy the worker using the steps above
2. Monitor logs to ensure it's processing events
3. Set up monitoring/alerts if needed
4. Consider scaling if you need more throughput

