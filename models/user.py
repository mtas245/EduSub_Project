from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
import enum
from database import Base

class Role(enum.Enum):
    ADMIN = 'admin'
    TEACHER = 'teacher'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(Integer, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SAEnum(Role), nullable=False, default=Role.TEACHER)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f'<User {self.email} ({self.role.value})>'
