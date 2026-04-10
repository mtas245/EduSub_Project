from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)

    personal_number = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    subjects = Column(String, nullable=True)
    bio = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())