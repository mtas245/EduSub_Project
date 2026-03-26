from sqlalchemy import Column, Integer, String, Enum as SAEnum
import enum
from database import Base

class role(enum.Enum):
    ADMIN = 'admin'
    TEACHER = 'teacher'

class User(Base):
    __tablename__ = 'users'
    id            = Column(Integer, primary_key=True)
    email         = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name     = Column(String, nullable=False)
    role          = Column(SAEnum(Role), nullable=False, default=Role.TEACHER)
    