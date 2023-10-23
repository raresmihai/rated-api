from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from contextlib import contextmanager

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/rated"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

metadata = MetaData()

active_session = None

@contextmanager
def get_db_session():
    global active_session

    if active_session is None or not active_session.is_active:
        active_session = SessionLocal()

    try:
        yield active_session
    except InvalidRequestError:
        active_session = SessionLocal()
        yield active_session
    finally:
        pass

def table_exists(table_name: str) -> bool:
    return engine.dialect.has_table(engine, table_name)

def init_db():
    if not table_exists("processed_transaction"):
        Base.metadata.create_all(bind=engine)
