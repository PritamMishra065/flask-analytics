# Flask Analytics Application

A high-performance analytics system built with Flask that ingests events asynchronously and provides real-time statistics. The system uses Redis as a message queue for asynchronous event processing and SQLAlchemy for database operations.

## Table of Contents

- [Architecture Decision](#architecture-decision)
- [Database Schema](#database-schema)
- [Setup Instructions](#setup-instructions)
- [API Usage](#api-usage)

---

## Architecture Decision

### Asynchronous Processing with Redis Queue

The application implements asynchronous event processing using **Redis** as a message queue. Here's how it works and why:

#### Implementation

1. **Event Ingestion (Fast Path)**: When a client sends an event to `POST /event`, the Flask application:
   - Validates the incoming event data
   - Immediately pushes the event JSON to a Redis list (queue) using `LPUSH`
   - Returns a `202 Accepted` response to the client

2. **Event Processing (Background)**: A separate worker process (`worker.py`) continuously:
   - Blocks on the Redis queue using `BRPOP` (blocking right-pop)
   - Retrieves events from the queue
   - Parses and validates the event data
   - Inserts the event into the database using SQLAlchemy

#### Why This Architecture?

**Benefits:**

1. **Low Latency**: The API responds immediately (typically < 10ms) without waiting for database writes, providing a better user experience
2. **Scalability**: Multiple worker processes can consume from the same queue, allowing horizontal scaling
3. **Resilience**: If the database is temporarily unavailable, events remain in the queue and can be processed later
4. **Decoupling**: The web server and database operations are decoupled, allowing independent scaling
5. **High Throughput**: Can handle thousands of events per second by batching database writes

**Trade-offs:**

- **Eventual Consistency**: There's a small delay (typically seconds) between event ingestion and when it appears in statistics
- **Queue Management**: Requires monitoring Redis queue length to prevent memory issues
- **Complexity**: Requires running and managing a separate worker process

This architecture is ideal for analytics workloads where high write throughput and low API latency are more important than immediate consistency.

---

## Database Schema

### Events Table

The application uses a single `events` table to store all analytics events:

```
┌─────────────────────────────────────────┐
│              events                     │
├─────────────────────────────────────────┤
│ id              INTEGER (Primary Key)   │
│ site_id         VARCHAR(255) NOT NULL   │
│ event_type      VARCHAR(255) NOT NULL   │
│ path            VARCHAR(500) NULL        │
│ user_id         VARCHAR(255) NULL        │
│ timestamp       DATETIME NOT NULL        │
└─────────────────────────────────────────┘
```

#### Field Descriptions

- **id**: Auto-incrementing primary key
- **site_id**: Identifier for the website/application (required)
- **event_type**: Type of event (e.g., "pageview", "click", "purchase") (required)
- **path**: URL path where the event occurred (optional)
- **user_id**: Identifier for the user who triggered the event (optional)
- **timestamp**: When the event occurred (UTC, required)

#### Example Data

```
id | site_id | event_type | path      | user_id | timestamp
---+---------+------------+-----------+---------+--------------------------
1  | site123 | pageview   | /home     | user456 | 2024-01-15 10:30:00
2  | site123 | click      | /products | user456 | 2024-01-15 10:31:00
3  | site123 | pageview   | /about    | user789 | 2024-01-15 10:32:00
```

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Redis server (version 6.0+ recommended)
- MySQL/MariaDB or TiDB database
- pip (Python package manager)

### Step 1: Clone and Navigate to Project

```bash
cd flask-analytics
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Redis

**Option A: Local Redis Installation**

- **Windows**: Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases) or use WSL
- **Linux**: `sudo apt-get install redis-server` (Ubuntu/Debian) or `sudo yum install redis` (CentOS/RHEL)
- **Mac**: `brew install redis`

Start Redis:
```bash
# On Linux/Mac
redis-server

# On Windows (if installed)
redis-server
```

**Option B: Redis Cloud (Production)**

Use a managed Redis service like:
- Redis Cloud (redis.com)
- AWS ElastiCache
- Azure Cache for Redis

### Step 5: Set Up Database

**Option A: Local MySQL/MariaDB**

1. Install MySQL or MariaDB
2. Create a database:
```sql
CREATE DATABASE analytics_db;
CREATE USER 'analytics_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON analytics_db.* TO 'analytics_user'@'localhost';
FLUSH PRIVILEGES;
```

**Option B: TiDB Cloud (Production)**

1. Create a TiDB Cloud account
2. Create a cluster and get connection details
3. Download the CA certificate if using SSL

### Step 6: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_QUEUE_NAME=event_queue

# Database Configuration
DATABASE_URL=mysql+pymysql://analytics_user:your_password@localhost:3306/analytics_db

# SSL Configuration (for TiDB Cloud or SSL-enabled databases)
TIDB_CA_PATH=./tidb-ca.pem
FORCE_SSL=false
```

**Important Notes:**
- Replace `your_password` with your actual database password
- For TiDB Cloud, use the connection string provided in the dashboard
- If using SSL, set `TIDB_CA_PATH` to the path of your CA certificate file
- For local MySQL without SSL, you can omit `TIDB_CA_PATH` and set `FORCE_SSL=false`

### Step 7: Initialize Database Tables

```bash
python create_tables.py
```

You should see: `Tables created!`

### Step 8: Start the Worker Process

Open a **new terminal window** and activate your virtual environment:

```bash
# Activate venv (if not already activated)
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

python worker.py
```

You should see: `Worker started and connected successfully!`

**Keep this terminal open** - the worker needs to run continuously.

### Step 9: Start the Flask Application

Open **another terminal window** and activate your virtual environment:

```bash
# Activate venv (if not already activated)
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

python app.py
```

You should see Flask starting on `http://0.0.0.0:5000`

### Step 10: Verify Installation

1. Open your browser and navigate to: `http://localhost:5000`
2. You should see the Analytics Dashboard
3. Try sending a test event using the form on the page

### Troubleshooting

**Redis Connection Error:**
- Ensure Redis is running: `redis-cli ping` (should return `PONG`)
- Check `REDIS_URL` in your `.env` file

**Database Connection Error:**
- Verify database credentials in `.env`
- Ensure database server is running
- Check network connectivity to database

**Worker Not Processing Events:**
- Ensure worker process is running
- Check Redis connection
- Verify `REDIS_QUEUE_NAME` matches in both `app.py` and `worker.py`

---

## API Usage

### Base URL

```
http://localhost:5000
```

### POST /event

Ingest a new analytics event. The event is queued for asynchronous processing.

#### Request

```bash
curl -X POST http://localhost:5000/event \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "example-site",
    "event_type": "pageview",
    "path": "/home",
    "user_id": "user123",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

#### Minimal Request (timestamp auto-generated)

```bash
curl -X POST http://localhost:5000/event \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "example-site",
    "event_type": "pageview"
  }'
```

#### Response

**Success (202 Accepted):**
```json
{
  "status": "accepted"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "site_id required"
}
```

#### Example: Multiple Event Types

```bash
# Pageview event
curl -X POST http://localhost:5000/event \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "example-site",
    "event_type": "pageview",
    "path": "/products",
    "user_id": "user456"
  }'

# Click event
curl -X POST http://localhost:5000/event \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "example-site",
    "event_type": "click",
    "path": "/products/item-123",
    "user_id": "user456"
  }'

# Purchase event
curl -X POST http://localhost:5000/event \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "example-site",
    "event_type": "purchase",
    "path": "/checkout",
    "user_id": "user456"
  }'
```

### GET /stats

Retrieve analytics statistics for a specific site and date.

#### Request

```bash
# Get stats for today
curl "http://localhost:5000/stats?site_id=example-site"

# Get stats for a specific date
curl "http://localhost:5000/stats?site_id=example-site&date=2024-01-15"
```

#### Response

**Success (200 OK):**
```json
{
  "site_id": "example-site",
  "date": "2024-01-15",
  "total_views": 1250,
  "unique_users": 342,
  "top_paths": [
    {
      "path": "/home",
      "views": 450
    },
    {
      "path": "/products",
      "views": 320
    },
    {
      "path": "/about",
      "views": 180
    }
  ]
}
```

**Error (400 Bad Request):**
```json
{
  "error": "site_id required"
}
```

#### Example: Query Different Dates

```bash
# Today's stats
curl "http://localhost:5000/stats?site_id=example-site"

# Yesterday's stats
curl "http://localhost:5000/stats?site_id=example-site&date=2024-01-14"

# Last week's stats
curl "http://localhost:5000/stats?site_id=example-site&date=2024-01-08"
```

### Complete Workflow Example

```bash
# 1. Send multiple events
curl -X POST http://localhost:5000/event \
  -H "Content-Type: application/json" \
  -d '{"site_id": "test-site", "event_type": "pageview", "path": "/home", "user_id": "user1"}'

curl -X POST http://localhost:5000/event \
  -H "Content-Type: application/json" \
  -d '{"site_id": "test-site", "event_type": "pageview", "path": "/about", "user_id": "user1"}'

curl -X POST http://localhost:5000/event \
  -H "Content-Type: application/json" \
  -d '{"site_id": "test-site", "event_type": "pageview", "path": "/home", "user_id": "user2"}'

# 2. Wait a few seconds for worker to process

# 3. Query stats
curl "http://localhost:5000/stats?site_id=test-site"
```

### Web Dashboard

The application also provides a web dashboard at `http://localhost:5000` where you can:
- Query statistics visually
- Send test events through a form
- View real-time analytics

---

## Production Deployment Considerations

### Process Management

Use a process manager to keep services running:

- **systemd** (Linux): Create service files for Flask app and worker
- **supervisor**: Process control system
- **PM2**: Node.js process manager (can run Python scripts)
- **Docker Compose**: Container orchestration

### Environment Variables

Never commit `.env` files. Use:
- Environment variables in your hosting platform
- Secret management services (AWS Secrets Manager, HashiCorp Vault)
- CI/CD pipeline secrets

### Monitoring

- Monitor Redis queue length to prevent memory issues
- Set up database connection pooling
- Add logging and error tracking (Sentry, LogRocket)
- Monitor worker process health

### Scaling

- Run multiple worker processes to increase throughput
- Use Redis Cluster for high availability
- Consider database read replicas for stats queries
- Use a load balancer for multiple Flask instances

---

## License

This project is provided as-is for educational and development purposes.

