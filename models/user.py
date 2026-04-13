from sqlalchemy import Column, Integer, String, Enum as SAEnum, DateTime
from sqlalchemy.sql import func
import enum
from database import Base

class Role(enum.Enum):
    ADMIN = 'admin'
    TEACHER = 'teacher'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SAEnum(Role), nullable=False, default=Role.TEACHER)

    # Profile fields
    personal_number = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    subjects = Column(String, nullable=True)  # comma-separated list of subjects
    bio = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f'<User {self.email} ({self.role.value})>'
    

