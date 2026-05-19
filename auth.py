import bcrypt
import random
from sqlmodel import Session, select
from models.user import User, Role

def hash_password(plain: str) -> str:
    """Hash a plain text password using bcrypt."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Check if a plain password matches the stored hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def register_user(
        db: Session,
        email: str,
        full_name: str,
        password: str,
        role: str,
        phone: str | None = None,
        documents_path: str | None = None
) -> User | None:
    """Creates a new user in the database.
    Returns None if email already exists."""
    existing = db.exec(select(User).where(User.email == email)).first()
    if existing:
        return None
    
    is_approved = Role(role) == Role.ADMIN
    
    new_user = User(
        email=email,
        full_name=full_name,
        password_hash=hash_password(password),
        role=Role(role),
        phone=phone,
        documents_path=documents_path,
        is_approved=is_approved,
    )
    db.add(new_user)
    db.flush()

    new_user.personal_number = generate_personal_number(db)

    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, email: str, password: str) -> User | None:
    """Verify credentials and return the User object.
    Returns None if credentials are wrong."""
    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if user.role == Role.TEACHER and not user.is_approved:
        return None
    return user

def generate_personal_number(db: Session) -> str:
    year = 2026
    while True:
        number = random.randint(1000, 9999)
        candidate = f'LP-{year}-{number}'
        existing = db.exec(
            select(User).where(User.personal_number == candidate)
        ).first()
        if not existing:
            return candidate
        