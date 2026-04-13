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
    #applications = relationship('Application', back_populates='request',
                                  #  cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Request {self.subject} @ {self.school_name} on {self.date} >'
    
    # Grade_Levels used in dropdowns and validation
    # 2 years Kindergarten + 6 years Primary (grades 1-6)
    GRADE_LEVELS = [
        # Kindergarten
        'KG1', 'KG2',
        # Primary Grade 1
        '1a', '1b',
        # Primary Grade 2
        '2a', '2b',
        # Primary Grade 3 (French added)
        '3a', '3b',
        # Primary Grade 4
        '4a', '4b',
        # Primary Grade 5 (English added)
        '5a', '5b',
        # Primary Grade 6
        '6a', '6b'
    ]

class SubstituteRequest(Base):
    __tablename__ = 'substitue_requests'

    id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    subject = Column(String, nullable=False)
    grade_level =Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time_slot = Column(String, nullable=True) # e.g. 08:00-12:00
    note = Column(String, nullable=True)
    status = Column(String, default='OPEN') # OPEN / FILLED / CANCELLED

    created_at = Column(DateTime, server_default=func.now())
    expires_at= Column(DateTime, nullable=True) # 12h before assignment start