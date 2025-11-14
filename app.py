# app.py
import os
import json
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import redis
from sqlalchemy import select, func, and_
from models import init_db, get_sessionmaker, Event

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
REDIS_QUEUE = os.getenv("REDIS_QUEUE_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")

r = redis.from_url(REDIS_URL, decode_responses=True)
SessionLocal = get_sessionmaker(DATABASE_URL)
init_db(DATABASE_URL)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/event", methods=["POST"])
def ingest():
    data = request.get_json(force=True)
    
    if not data.get("site_id"):
        return jsonify({"error": "site_id required"}), 400
    if not data.get("event_type"):
        return jsonify({"error": "event_type required"}), 400
    
    if not data.get("timestamp"):
        data["timestamp"] = datetime.utcnow().isoformat() + "Z"

    r.lpush(REDIS_QUEUE, json.dumps(data))
    return jsonify({"status": "accepted"}), 202


@app.route("/stats", methods=["GET"])
def stats():
    site_id = request.args.get("site_id")
    if not site_id:
        return jsonify({"error": "site_id required"}), 400

    date_str = request.args.get("date")
    if date_str:
        try:
            target_date = datetime.fromisoformat(date_str).date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    else:
        target_date = date.today()

    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())

    session = SessionLocal()

    try:
        # Count total views (all events for the site_id and date)
        total_views = session.execute(
            select(func.count(Event.id)).where(
                and_(
                    Event.site_id == site_id,
                    Event.timestamp >= start,
                    Event.timestamp <= end
                )
            )
        ).scalar_one() or 0

        # Count unique users
        unique_users = session.execute(
            select(func.count(func.distinct(Event.user_id))).where(
                and_(
                    Event.site_id == site_id,
                    Event.timestamp >= start,
                    Event.timestamp <= end,
                    Event.user_id.isnot(None)
                )
            )
        ).scalar_one() or 0
        
        # Get top paths with view counts
        top_paths_result = session.execute(
            select(Event.path, func.count(Event.id).label('view_count'))
            .where(
                and_(
                    Event.site_id == site_id,
                    Event.timestamp >= start,
                    Event.timestamp <= end,
                    Event.path.isnot(None)
                )
            )
            .group_by(Event.path)
            .order_by(func.count(Event.id).desc())
            .limit(10)
        ).all()

        top_paths = [{"path": p or "/", "views": v} for p, v in top_paths_result]

        return jsonify({
            "site_id": site_id,
            "date": target_date.isoformat(),
            "total_views": total_views,
            "unique_users": unique_users,
            "top_paths": top_paths
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST"),
        port=int(os.getenv("FLASK_PORT")),
        debug=True
    )
