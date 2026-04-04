from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.sql import func
from db.base import Base


class MessageUsageCreditLog(Base):
    __tablename__ = "message_usage_credit_logs"

    usage_id = Column(String, primary_key=True, index=True)
    busi_user_id = Column(String, nullable=False, index=True)
    message_id = Column(String, nullable=False, index=True)
    credits_deducted = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
