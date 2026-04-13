from sqlalchemy.orm import Session
from models.user import User

class ProfileService:

    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_profile(self, user_id: int, **kwargs) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_profile(self, user_id: int, **kwargs) -> User | None:
        """"
        Updates allowed fields only.
        personal_number and email are intentionally excluded.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        for field in ['full_name', 'phone', 'subjects', 'bio']:
            if field in kwargs:
                setattr(user, field, kwargs[field])
        self.db.commit()
        self.db.refresh(user)
        return user