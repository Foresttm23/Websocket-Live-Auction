from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from database import Base
import enum


class LotStatus(str, enum.Enum):
    running = "running"
    ended = "ended"


class Lot(Base):
    __tablename__ = "lots"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    start_price = Column(Numeric, default=1)
    status = Column(Enum(LotStatus), default=LotStatus.running)

    start_time = Column(DateTime, default=datetime.utcnow)  # Basically unused, but overall can be good for tracking
    end_time = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(seconds=60))

    bids = relationship("Bid", back_populates="lot")


class Bid(Base):
    __tablename__ = "bids"
    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(Integer, ForeignKey("lots.id"))
    bidder = Column(String)
    amount = Column(Numeric)

    lot = relationship("Lot", back_populates="bids")
