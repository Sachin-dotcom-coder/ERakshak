import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("postgresql://postgres.kclwyeskjpazesycrpmo:npZVKRC5NgM1LTEu@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")

connect_args = {}
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args) if DATABASE_URL else create_engine("sqlite:///./sql_app.db", connect_args={"check_same_thread": False})
    with engine.connect() as conn:
        pass
except Exception as e:
    print(f"Warning: Primary database connection failed ({e}). Falling back to local SQLite database.")
    DATABASE_URL = "sqlite:///./sql_app.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import models
Base.metadata.create_all(bind=engine)

