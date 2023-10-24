from sqlalchemy import create_engine, inspect, Column, String, Integer, Float, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from contextlib import contextmanager

#DATABASE_URL = "postgresql://postgres:user@password:5432/rated"

# Using SQLite in-memory database
DATABASE_URL = "sqlite:///ratedapi.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

metadata = MetaData()

@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def table_exists(table_name: str) -> bool:
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def init_db():
    if not table_exists("processed_transaction"):
        Base.metadata.create_all(bind=engine)
