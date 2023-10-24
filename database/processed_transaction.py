from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

from .database import Base

class ProcessedTransaction(Base):
    """
    A SQLAlchemy model representing a processed transaction.
    """

    __tablename__ = "processed_transaction"

    hash = Column(String, primary_key=True, unique=True, index=True)
    fromAddress = Column(String)
    toAddress = Column(String)
    blockNumber = Column(Integer)
    executedAt = Column(DateTime)
    gasUsed = Column(Integer)
    gasCostInDollars = Column(Float)
