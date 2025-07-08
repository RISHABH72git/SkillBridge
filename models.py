import uuid
from sqlalchemy import Column, String, CHAR, Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(500))
    is_active = Column(Boolean, default=True)
    user_type = Column(String(100))
    jobs = relationship("Jobs", back_populates="recruiter")

class Jobs(Base):
    __tablename__ = "jobs"
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String(100))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    company_name = Column(String(200))
    pincode = Column(Integer)
    city = Column(String(100))
    country = Column(String(100))
    recruiter_id = Column(CHAR(36), ForeignKey("users.id"))
    recruiter = relationship("User", back_populates="jobs")