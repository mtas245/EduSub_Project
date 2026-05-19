from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "sqlite:///edusub.db"

engine = create_engine(DATABASE_URL, echo=False)

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def SessionLocal():
    return Session(engine)
