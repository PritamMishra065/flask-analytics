import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
TIDB_CA_PATH = os.getenv("TIDB_CA_PATH") or None
FORCE_SSL = os.getenv("FORCE_SSL", "false").lower() in ("1","true","yes")

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(String(255), nullable=False)
    event_type = Column(String(255), nullable=False)
    path = Column(String(500), nullable=True)
    user_id = Column(String(255), nullable=True)
    timestamp = Column(DateTime, nullable=False)

def build_connect_args():
    if TIDB_CA_PATH:
        return {"ssl": {"ca": TIDB_CA_PATH}}
    if FORCE_SSL:
        return {"ssl": {}}
    return {}

def main():
    print("DATABASE_URL =", DATABASE_URL)
    connect_args = build_connect_args()
    print("Using connect_args =", connect_args)
    engine = create_engine(DATABASE_URL, future=True, connect_args=connect_args)
    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    main()
