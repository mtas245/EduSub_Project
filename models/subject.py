from typing import Optional
from sqlmodel import Field, SQLModel

class Subject(SQLModel, table=True):
    __tablename__ = 'subjects'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)
    level: str = Field(nullable=False)
    grades: Optional[str] = Field(default=None)

    def __repr__(self) -> str:
        return f'<Subject {self.name} ({self.level})>'
    
class UserSubject(SQLModel, table=True):
    __tablename__ = 'user_subjects'

    user_id: int = Field(foreign_key='users.id', primary_key=True)
    subject_id: int = Field(foreign_key='subjects.id', primary_key=True)

DEFAULT_SUBJECTS = [
    # Kindergarten
    {'name': 'Free Play', 'level': 'Kindergarten', 'grades': 'KG1,KG2'},
    {'name': 'Movement', 'level': 'Kindergarten', 'grades': 'KG1,KG2'},
    {'name': 'Crafts', 'level': 'Kindergarten', 'grades': 'KG1,KG2'},
    # Primary
    {'name': 'German', 'level': 'Primary', 'grades': '1,2,3,4,5,6'},
    {'name': 'Mathematics', 'level': 'Primary', 'grades': '1,2,3,4,5,6'},
    {'name': 'LNMG', 'level': 'Primary', 'grades': '1,2,3,4,5,6'},
    {'name': 'Textiles & Crafts', 'level': 'Primary', 'grades': '1,2,3,4,5,6'},
    {'name': 'Art (BG)', 'level': 'Primary', 'grades': '1,2,3,4,5,6'},
    {'name': 'PE', 'level': 'Primary', 'grades': '1,2,3,4,5,6'},
    {'name': 'Music', 'level': 'Primary', 'grades': '1,2,3,4,5,6'},
    {'name': 'French', 'level': 'Primary', 'grades': '3,4,5,6'},
    {'name': 'English', 'level': 'Primary', 'grades': '5,6'},
]


