import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
url = os.getenv("DATABASE_URL")
ca = os.getenv("TIDB_CA_PATH") or None
force = os.getenv("FORCE_SSL", "false").lower() in ("1","true","yes")
connect_args = {"ssl": {"ca": ca}} if ca else ({"ssl": {}} if force else {})

print("DATABASE_URL:", url)
print("TIDB_CA_PATH:", ca)
print("Connect args:", connect_args)

try:
    engine = create_engine(url, connect_args=connect_args)
    with engine.connect() as conn:
        print("Connected OK. Server version:", conn.execute(text("SELECT VERSION()")).scalar())
except Exception as e:
    import traceback; traceback.print_exc()
