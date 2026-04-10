# services/profile_service.py
from sqlalchemy.orm import Session
from models.user import User

class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: int) -> User: | None:
    return self.db.query(User).filter(User.id == user_id).first()

def update_profile(self, user_id, **kwargs) -> User | None:
    '''
    Updates allowed fields only.
    personal_number and email are intentionally excluded.
    '''
    user = self.get_profile(user_id)
    if not user:
        return None
    allowed = {'full_name', 'phone', 'subjects', 'bio'}
    for field, value in kwargs.items():
        if field in allowed:
            setattr(user, field, value)
            self.db.commit()
            self.db.refresh(user)
            return user


