from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
import enum


class RequestStatus(str, enum.Enum):
    OPEN = 'open'
    FILLED = 'filled'
    CANCELLED = 'cancelled'

GRADE_LEVELS = [
    'KG1', 'KG2',
    '1a', '1b', '2a', '2b',
    '3a', '3b', '4a', '4b',
    '5a', '5b', '6a', '6b'
]

class SubstituteRequest(SQLModel, table=True):
    __tablename__ = 'substitute_requests'

    id: Optional[int] = Field(default=None, primary_key=True)
    created_by: int = Field(foreign_key='users.id', nullable=False)
    subject: str = Field(nullable=False)
    grade_level: str = Field(nullable=False)
    date: datetime = Field(nullable=False)
    time_slot: Optional[str] = Field(default=None)  # e.g. "08:00-12:00"
    note: Optional[str] = Field(default=None)
    status: RequestStatus = Field(default=RequestStatus.OPEN)
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(default=None)

    def __repr__(self):
        return f'<Request {self.subject} {self.grade_level} on {self.date}>'
    