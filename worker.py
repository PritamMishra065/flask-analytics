# worker.py
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Event

# Load environment variables
load_dotenv()

# Read environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
REDIS_QUEUE = os.getenv("REDIS_QUEUE_NAME")
TIDB_CA_PATH = os.getenv("TIDB_CA_PATH")

# Debug print for verification
print("DEBUG: DATABASE_URL =", DATABASE_URL)
print("DEBUG: TIDB_CA_PATH =", TIDB_CA_PATH)
print("DEBUG: REDIS_URL =", REDIS_URL)
print("DEBUG: REDIS_QUEUE =", REDIS_QUEUE)

# SSL settings for TiDB Cloud (same logic as models.py)
def _build_connect_args():
    """Build connect_args based on SSL configuration"""
    if TIDB_CA_PATH:
        return {"ssl": {"ca": TIDB_CA_PATH}}
    FORCE_SSL = os.getenv("FORCE_SSL", "false").lower() in ("1", "true", "yes")
    if FORCE_SSL:
        return {"ssl": {}}
    return {}

# Create SQLAlchemy engine + session
connect_args = _build_connect_args()
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)

# Redis connection
r = redis.from_url(REDIS_URL, decode_responses=True)

# Event parser
def parse_event(data):
    try:
        ts = data["timestamp"].replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
    except:
        dt = datetime.utcnow()

    return Event(
        site_id=data["site_id"],
        event_type=data["event_type"],
        path=data.get("path"),
        user_id=data.get("user_id"),
        timestamp=dt
    )

def main():
    print("Worker started and connected successfully!")
    while True:
        item = r.brpop(REDIS_QUEUE, timeout=5)
        if not item:
            continue

        _, raw = item
        data = json.loads(raw)
        print("Processing:", data)

        session = SessionLocal()
        event = parse_event(data)
        session.add(event)
        session.commit()
        session.close()

if __name__ == "__main__":
    main()
