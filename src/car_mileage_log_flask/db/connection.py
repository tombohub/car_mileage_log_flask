import os

import records
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(override=True)

db_url = os.getenv("DATABASE_URL")
assert db_url, "DATABASE_URL is not set"

engine = create_engine(db_url, echo=True)

db = records.Database(engine.url)

Session = sessionmaker(bind=engine)
session = Session()
