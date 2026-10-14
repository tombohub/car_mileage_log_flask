import os

import records
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(override=True)

db_url = os.getenv("DATABASE_URL")
assert db_url, "DATABASE_URL is not set"

if db_url.startswith("postgres://"):
    sqlalchemy_db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif db_url.startswith("postgresql://"):
    sqlalchemy_db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    sqlalchemy_db_url = db_url

engine = create_engine(sqlalchemy_db_url)

db = records.Database(engine.url)

Session = sessionmaker(bind=engine)
session = Session()
