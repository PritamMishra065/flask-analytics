# create_tables.py
import os
from dotenv import load_dotenv
from models import init_db

load_dotenv()
init_db(os.getenv("DATABASE_URL"))
print("Tables created!")
