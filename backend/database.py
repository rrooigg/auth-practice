from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from models import Base
import os

DATABASE_URL= 'postgresql+psycopg://postgres:1234@localhost:5432/users'

engine= create_engine(DATABASE_URL)

SessionLocal= sessionmaker(bind=engine, autoflush=False, autocommit=False)

metadata= MetaData()

def get_db():
  db= SessionLocal()
  try:
    yield db
  finally:
    db.close()

Base.metadata.create_all(bind=engine)

