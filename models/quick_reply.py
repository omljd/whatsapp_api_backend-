import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from db.base import Base

class QuickReply(Base):
    __tablename__ = "quick_replies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    busi_user_id = Column(UUID(as_uuid=True), ForeignKey("businesses.busi_user_id"), nullable=False)
    shortcut = Column(String, nullable=False) 
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
