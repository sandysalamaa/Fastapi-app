from sqlalchemy import Column , Integer , String , DateTime , ForeignKey
from datetime import datetime
from app.db.base import Base 

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer , primary_key=True)
    name = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)