from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from edu_match.app.infrastructure.db.database import DATABASE_URL, SessionLocal

DATABASE_URL = 'sqlite:///edumatch.db'

engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    '''Returns a DB session. Always close after use.'''
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

