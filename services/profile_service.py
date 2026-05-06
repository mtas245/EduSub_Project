from sqlmodel import Session, select
from models.user import User, Role
from models.subject import Subject, UserSubject


class ProfileService:

    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def update_profile(self, user_id: int, **kwargs) -> User | None:
        """
        Updates allowed fields only.
        personal_number and email are intentionally excluded.
        """
        user = self.db.get(User, user_id)
        if not user:
            return None
        for field in ['full_name', 'phone', 'bio', 'documents_path', 'profile_picture']:
            if field in kwargs:
                setattr(user, field, kwargs[field])
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_subjects(self, user_id: int) -> list[Subject]:
        """Returns all subjects assigned to a user."""
        user_subjects = self.db.exec(
            select(UserSubject).where(UserSubject.user_id == user_id)
        ).all()
        subject_ids = [us.subject_id for us in user_subjects]
        if not subject_ids:
            return []
        return self.db.exec(
            select(Subject).where(Subject.id.in_(subject_ids))
        ).all()

    def set_subjects(self, user_id: int, subject_ids: list[int]) -> None:
        """Replaces all subject assignments for a user."""
        existing = self.db.exec(
            select(UserSubject).where(UserSubject.user_id == user_id)
        ).all()
        for us in existing:
            self.db.delete(us)
        for sid in subject_ids:
            self.db.add(UserSubject(user_id=user_id, subject_id=sid))
        self.db.commit()

    def get_pending_teachers(self) -> list[User]:
        """Returns all teachers waiting for approval."""
        return self.db.exec(
            select(User)
            .where(User.role == Role.TEACHER, User.is_approved == False)
            .order_by(User.created_at.asc())
        ).all()

    def approve_teacher(self, user_id: int) -> bool:
        """Approves a teacher account. Returns True if successful."""
        user = self.db.get(User, user_id)
        if not user or user.role != Role.TEACHER:
            return False
        user.is_approved = True
        self.db.commit()
        return True

    def reject_teacher(self, user_id: int) -> bool:
        """Deletes a rejected teacher account. Returns True if successful."""
        user = self.db.get(User, user_id)
        if not user or user.role != Role.TEACHER:
            return False
        self.db.delete(user)
        self.db.commit()
        return True