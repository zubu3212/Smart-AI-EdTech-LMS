import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DEFAULT_SQLITE_DB = "sqlite:///./smart_edtech.db"

# Prefer an explicit DATABASE_URL when provided. If the project is being run locally
# without a real cloud database configured, fall back to a local SQLite database so
# the app can boot reliably in development environments.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL or "ep-xxx" in DATABASE_URL or DATABASE_URL.startswith("******"):
    DATABASE_URL = DEFAULT_SQLITE_DB

# Render or other cloud providers sometimes use the legacy postgres:// scheme.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs a dedicated connect_args configuration; other DBs can use pool_pre_ping.
engine_kwargs = {"echo": False}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# FastAPI dependency injection for database sessions.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
