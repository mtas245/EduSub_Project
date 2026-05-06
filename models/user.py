from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
import enum

class Role(str, enum.Enum):
    ADMIN = 'admin'
    TEACHER = 'teacher'

class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(nullable=False, unique=True)
    password_hash: str = Field(nullable=False)
    full_name: str = Field(nullable=False)
    role: Role = Field(default=Role.TEACHER)

    personal_number: Optional[str] = Field(default=None, unique=True)
    phone: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    documents_path: Optional[str] = Field(default=None)
    is_approved: bool = Field(default=False)

    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
    