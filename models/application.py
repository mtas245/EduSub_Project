# models/application.py
# Temporary empty file — Member C will fill this
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base


class ApplicationStatus(enum.Enum):
    PENDING  = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class Application(Base):
    __tablename__ = 'applications'
    id         = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    request_id = Column(Integer, ForeignKey('substitute_requests.id'), nullable=False)
    status     = Column(SAEnum(ApplicationStatus), default=ApplicationStatus.PENDING)
    applied_at = Column(DateTime, server_default=func.now())