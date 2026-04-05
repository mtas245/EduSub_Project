from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class RequestStatus(enum.Enum):
    OPEN = 'open'
    FILLED = 'filled'

class SubstituteRequest(Base):
    __tablename__ = 'substitute_requests'

    id              = Column(Integer, primary_key=True, index=True)
    school_name       = Column(String, nullable=False)
    subject           = Column(String, nullable=False)
    grade_level       = Column(String, nullable=False)
    date              = Column(Date, nullable=False)
    note = Column(String, nullable=True)
    status            = Column(SAEnum(RequestStatus), nullable=False, default=RequestStatus.OPEN)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    creator = relationship('User', backref='requests')
    applications = relationship('Application', back_populates='request',
                                    cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Request {self.subject} @ {self.school_name} on {self.date} >'
    