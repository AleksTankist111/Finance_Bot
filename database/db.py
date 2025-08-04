from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from config import SQL_DB

engine = create_engine(SQL_DB, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
