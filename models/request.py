from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
import enum

class RequestStatus(str, enum.Enum):
    OPEN = 'open'
    FILLED = 'filled'
    CANCELLED = 'cancelled'

GRADE_LEVELS: list[str] = [
    'KG1', 'KG2',
    '1a', '1b', '2a', '2b',
    '3a', '3b', '4a', '4b',
    '5a', '5b', '6a', '6b',
]

class SubstituteRequest(SQLModel, table=True):
    __tablename__ = 'substitute_requests'

    id: Optional[int] = Field(default=None, primary_key=True)
    created_by: int = Field(foreign_key='users.id', nullable=False)
    subject_id: int = Field(foreign_key='subjects.id', nullable=False)
    grade_level: str = Field(nullable=False)
    date: datetime = Field(nullable=False)
    time_slot: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    status: RequestStatus = Field(default=RequestStatus.OPEN)
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(default=None)

    def __repr__(self) -> str:
        return (
            f"SubstituteRequest("
            f"id={self.id}, "
            f"subject_id={self.subject_id}, "
            f"grade_level='{self.grade_level}', "
            f"date={self.date}, "
            f"status={self.status.value!r})"
        )
    
    def __str__(self) -> str:
        return f"Request #{self.id} - Grade {self.grade_level} on {self.date}"
    
