from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.db.base import Base 

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    details = Column(JSONB) 
    created_at = Column(DateTime, default=datetime.utcnow)
