from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base
import datetime

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    api_url = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Source {self.name}>"

class Currency(Base):
    __tablename__ = "currencies"
    code = Column(String(3), primary_key=True)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<Currency {self.code}>"

class CurrencyPair(Base):
    __tablename__ = "currency_pairs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    base_currency = Column(String(3), ForeignKey("currencies.code"), nullable=False)
    target_currency = Column(String(3), ForeignKey("currencies.code"), nullable=False)
    
    # Add a unique constraint to prevent duplicate pairs
    __table_args__ = (UniqueConstraint('base_currency', 'target_currency', name='_base_target_uc'),)

    base = relationship("Currency", foreign_keys=[base_currency])
    target = relationship("Currency", foreign_keys=[target_currency])

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pair_id = Column(Integer, ForeignKey("currency_pairs.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    rate = Column(Float, nullable=False)

    pair = relationship("CurrencyPair")
    source = relationship("Source")
