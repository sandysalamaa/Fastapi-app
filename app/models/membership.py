from sqlalchemy import Column, Integer, ForeignKey, String
from app.db.base import Base


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"))
    role = Column(String, nullable=False)  # can beadmin or member