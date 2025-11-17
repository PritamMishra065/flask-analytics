# worker.py
import os
import json
import time
import sys
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

# SSL settings for TiDB Cloud
connect_args = {"ssl": {"ca": TIDB_CA_PATH}} if TIDB_CA_PATH else {}

# Create SQLAlchemy engine + session
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)

# Redis connection with SSL support for Upstash
# rediss:// protocol automatically enables SSL, but we need to configure it properly
if REDIS_URL and REDIS_URL.startswith('rediss://'):
    # Upstash Redis with SSL
    import ssl
    r = redis.from_url(
        REDIS_URL,
        decode_responses=True,
        ssl_cert_reqs=ssl.CERT_NONE  # Upstash doesn't require client certificates
    )
else:
    # Regular Redis without SSL
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
    # Support --max-events argument for one-off runs (e.g., python worker.py --max-events 100)
    max_events = None
    if len(sys.argv) > 2 and sys.argv[1] == "--max-events":
        try:
            max_events = int(sys.argv[2])
        except ValueError:
            pass
    
    processed = 0
    print("Worker started and connected successfully!")
    
    while True:
        # For one-off runs: exit after processing max_events
        if max_events and processed >= max_events:
            print(f"Reached max events limit ({max_events}). Exiting.")
            break
        
        # Always use blocking pop with timeout for continuous operation
        item = r.brpop(REDIS_QUEUE, timeout=5)
        
        if not item:
            # For one-off runs: exit if queue is empty
            if max_events:
                print(f"Queue empty after processing {processed} events. Exiting.")
                break
            # Continuous mode: just wait and retry
            continue

        _, raw = item
        data = json.loads(raw)
        print("Processing:", data)

        session = SessionLocal()
        event = parse_event(data)
        session.add(event)
        session.commit()
        session.close()
        processed += 1
        print(f"Processed {processed} events total")

if __name__ == "__main__":
    main()
