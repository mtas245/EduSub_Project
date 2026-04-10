import bcrypt
from sqlalchemy.orm import Session
from models.user import User, Role
import random
from sqlalchemy.orm import Session
from models.user import User

def hash_password(plain: str) -> str:
    '''Hash a plain text password using bcyrpt'''
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    '''Check if a plain text password matches the stored hash.'''
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def register_user(db: Session, email: str, full_name: str,
                  password: str, role: str) -> User | None:
    '''Create a new user in the database.
    Returns None if email already exists.'''
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return None # if email taken
    new_user = User(
        email=email,
        full_name=full_name,
        password_hash=hash_password(password),
        role=Role(role)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, email: str, password: str) -> User | None:
    '''
    Verify credentials and return the User object.
    Returns None if credentials are wrong.
    '''
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def generate_personal_number(db: Session) -> str:
    year = 2026
    while True:
        number = random.randint(1000, 9999)
        candidate = f'LP-{year}-{number}'
        existing = db.query(User).filter(
            User.personal_number == candidate
        ).first()
        if not existing:
            return candidate