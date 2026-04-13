from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class RequestStatus(enum.Enum):
    OPEN = 'open'
    FILLED = 'filled'
    CANCELLED = 'cancelled'

GRADE_LEVELS = [
    'KG1', 'KG2',
    '1a', '1b', '2a', '2b',
    '3a', '3b', '4a', '4b',
    '5a', '5b', '6a', '6b'
]

class SubstituteRequest(Base):
    __tablename__ = 'substitute_requests'

    id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String, nullable=False)
    grade_level = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    time_slot = Column(String, nullable=True)  # e.g. "08:00-12:00"
    note = Column(String, nullable=True)
    status = Column(SAEnum(RequestStatus), default=RequestStatus.OPEN, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

    creator = relationship('User', backref='requests')

    def __repr__(self):
        return f'<Request {self.subject} {self.grade_level} on {self.date}>'
    