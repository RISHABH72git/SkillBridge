import uuid
from sqlalchemy import Column, String, CHAR, Boolean
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(500))
    is_active = Column(Boolean, default=True)
    user_type = Column(String(100))
