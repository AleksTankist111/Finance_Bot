from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from config import DEFAULT_CURRENCY

Base = declarative_base()


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_deleted = Column(Boolean, default=False)
    # TODO: Add non-necessary field "from_source_id" for proper work of transfer operations ???


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_deleted = Column(Boolean, default=False)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    currency = Column(String, default=DEFAULT_CURRENCY)
    is_income = Column(Boolean)
    source_id = Column(Integer, ForeignKey("sources.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    comment = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

    source = relationship("Source")
    category = relationship("Category")
