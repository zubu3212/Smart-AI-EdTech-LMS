import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# আপনার PostgreSQL-এর আসল পাসওয়ার্ড দিন
DB_USER = "postgres"
DB_PASSWORD = "5080"  # <--- পাসওয়ার্ড বসান
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "edtech_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()