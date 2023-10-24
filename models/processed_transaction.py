from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from database.database import Base

class ProcessedTransaction(Base):
    __tablename__ = "processed_transaction"

    hash = Column(String, primary_key=True, unique=True, index=True)
    fromAddress = Column(String)
    toAddress = Column(String)
    blockNumber = Column(Integer)
    executedAt = Column(DateTime)
    gasUsed = Column(Integer)
    gasCostInDollars = Column(Float)

    def __repr__(self):
        return (
            f"ProcessedTransaction(hash='{self.hash}', "
            f"fromAddress='{self.fromAddress}', "
            f"toAddress='{self.toAddress}', "
            f"blockNumber={self.blockNumber}, "
            f"executedAt={self.executedAt}, "
            f"gasUsed={self.gasUsed}, "
            f"gasCostInDollars={self.gasCostInDollars})"
        )
