import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ১. Neon PostgreSQL থেকে পাওয়া কানেকশন স্ট্রিং (Default Fallback হিসেবে দেওয়া হলো)
NEON_DATABASE_URL = "postgresql://neondb_owner:YOUR_NEON_PASSWORD@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"

# ২. Environment variable থেকে DATABASE_URL রিড করবে, না থাকলে Netlify DB বা Neon-এর URL নিবে
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("NETLIFY_DB_URL") or NEON_DATABASE_URL

# ৩. Render বা অন্য কোনো ক্লাউডে 'postgres://' থাকলে তা 'postgresql://' দিয়ে রিপ্লেস করা
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ৪. SQLAlchemy Engine এবং Session তৈরি
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # কানেকশন ড্রপ হওয়া রোধ করে
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 💡 FastAPI-র জন্য স্ট্যান্ডার্ড Dependency Injection get_db (yield সহ)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
