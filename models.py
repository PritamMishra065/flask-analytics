# models.py
import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
TIDB_CA_PATH = os.getenv("TIDB_CA_PATH")  # e.g. ./tidb-ca.pem
FORCE_SSL = os.getenv("FORCE_SSL", "false").lower() in ("1", "true", "yes")

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(String(255), nullable=False)
    event_type = Column(String(255), nullable=False)
    path = Column(String(500), nullable=True)
    user_id = Column(String(255), nullable=True)
    timestamp = Column(DateTime, nullable=False)

def _build_connect_args():
    """
    Return connect_args for pymysql:
      - if TIDB_CA_PATH provided => {'ssl': {'ca': '/path/to/ca.pem'}}
      - elif FORCE_SSL true => {'ssl': {}}
      - else => {}
    """
    if TIDB_CA_PATH:
        return {"ssl": {"ca": TIDB_CA_PATH}}
    if FORCE_SSL:
        return {"ssl": {}}
    return {}

def init_db(db_url=DATABASE_URL):
    connect_args = _build_connect_args()
    engine = create_engine(
        db_url,
        future=True,
        pool_size=5,
        max_overflow=10,
        connect_args=connect_args,
        echo=False,
    )
    Base.metadata.create_all(engine)
    return engine

def get_sessionmaker(db_url=DATABASE_URL):
    connect_args = _build_connect_args()
    engine = create_engine(db_url, future=True, connect_args=connect_args)
    return sessionmaker(bind=engine, future=True)
