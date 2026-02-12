from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent

load_dotenv()

AUTH_DATABASE_URL = os.getenv("AUTH_DATABASE_URL", f"sqlite:///{BASE_DIR}/auth_db.db")
# Only use check_same_thread for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in AUTH_DATABASE_URL else {}
engine = create_engine(AUTH_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
