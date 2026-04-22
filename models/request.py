from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
import enum

class RequestStatus(str, enum.Enum):
    """Enum representing the lifecycle status of a substitute request."""
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
    """"ORM model representing a substitute teacher request.
    
    Maps to the 'substitute_requests' table in the database.
    Each instance represents one open or resolved substitute assignment.
    """

    __tablename__ = 'substitute_requests'

    id: Optional[int] = Field(default=None, primary_key=True)
    created_by: int = Field(foreign_key='users.id', nullable=False)
    subject: str = Field(nullable=False)
    grade_level: str = Field(nullable=False)
    date: datetime = Field(nullable=False)
    time_slot: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    status: RequestStatus = Field(default=RequestStatus.OPEN)
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(default=None)

    def __repr__(self) -> str:
        return(
            f"SubstituteRequest("
             f"id={self.id}, "
            f"subject='{self.subject}', "
            f"grade_level='{self.grade_level}', "
            f"date={self.date}, "
            f"status={self.status.value!r})"
        )
    
    def __str__(self) -> str:
        """Human readable string representation used in UI labels and notifications."""
        return f"{self.subject} - {self.grade_level} on {self.date}"
    