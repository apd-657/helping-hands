# database.py
# This file sets up the database connection using SQLAlchemy ORM
# SQLite is a file-based database — no server setup needed!

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file will be created in the backend folder automatically
DATABASE_URL = "sqlite:///./helping_hands.db"

# Create the database engine
# check_same_thread=False is needed for SQLite with FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal is a factory for database sessions (one per request)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our database models (tables)
Base = declarative_base()

# Dependency function — used in every route to get a DB session
# It opens a session, yields it to the route, then closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
