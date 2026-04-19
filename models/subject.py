from typing import Optional
from sqlmodel import Field, SQLModel


class Subject(SQLModel, table=True):
    __tablename__ = 'subjects'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    level: str = Field(nullable=False)
    grades: Optional[str] = Field(default=None)

DEFAULT_SUBJECTS = [
    # Kindergarten (KG1, KG2)
    # No fixed curriculum (only free play and movement)
    {'name': 'Free Play', 'level': 'Kindergarten', 'grades': ['KG1', 'KG2']},
    {'name': 'Movement', 'level': 'Kindergarten', 'grades': ['KG1', 'KG2']},
    {'name': 'Crafts', 'level': 'Kindergarten', 'grades': ['KG1', 'KG2']},

    # Primary: all grades 1-6
    {'name': 'German', 'level': 'Primary', 'grades':
['1', '2','3','4','5','6']},
    {'name': 'Mathematics', 'level': 'Primary', 'grades':
['1', '2','3','4','5','6']},
    {'name': 'LNMG', 'level': 'Primary', 'grades':
['1', '2','3','4','5','6']},
    {'name': 'Textiles & Crafts', 'level': 'Primary', 'grades':
['1', '2','3','4','5','6']},
    {'name': 'Art (BG)', 'level': 'Primary', 'grades':
['1', '2','3','4','5','6']},
    {'name': 'PE', 'level': 'Primary', 'grades':
['1', '2','3','4','5','6']},
    {'name': 'Music', 'level': 'Primary', 'grades':
['1', '2','3','4','5','6']},

    # French: from Grade 3 onwards
    {'name': 'French', 'level': 'Primary', 'grades': ['3','4','5','6']},
    # English: from Grade 5 onwards
    {'name': 'English', 'level': 'Primary', 'grades': ['5','6']}]