from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
import enum


class ApplicationStatus(str, enum.Enum):
    PENDING  = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class Application(SQLModel, table=True):
    __tablename__ = 'applications'

    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key='users.id', nullable=False)
    request_id: int = Field(foreign_key='substitute_requests.id', nullable=False)
    status: ApplicationStatus = Field(default=ApplicationStatus.PENDING)
    applied_at: datetime = Field(default_factory=datetime.now)
