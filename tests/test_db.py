import pytest
from datetime import date
from sqlmodel import SQLModel, Session, create_engine, select

from models.user import User, Role
from models.request import SubstituteRequest, RequestStatus
from models.application import Application, ApplicationStatus
from models.subject import Subject

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_save_user_persists_in_database(db):
    user = User(
        full_name="Test Teacher",
        email="teacher@test.com",
        password_hash="hashed",
        role=Role.TEACHER,
        personal_number="LP-2026-0001",
    )
    db.add(user)
    db.commit()

    saved_user = db.exec(select(User).where(User.email == "teacher@test.com")).first()

    assert saved_user is not None
    assert saved_user.full_name == "Test Teacher"
    assert saved_user.role == Role.TEACHER

def test_save_substitute_request_persists_all_fields(db):
    admin = User(
        full_name="Admin",
        email="admin@test.com",
        password_hash="hashed",
        role=Role.ADMIN,
        personal_number="LP-2026-0002",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    subject = Subject(name="Mathematics", level="Primary", grades="1,2,3,4,5,6")
    db.add(subject)
    db.commit()
    db.refresh(subject)

    request = SubstituteRequest(
        created_by=admin.id,
        subject_id=subject.id,
        grade_level="3a",
        date=date(2026, 5, 20),
        time_slot="08:00-10:00",
        note="Bring books",
        status=RequestStatus.OPEN
    )
    db.add(request)
    db.commit()

    saved_request = db.exec(
        select(SubstituteRequest).where(SubstituteRequest.subject_id == subject.id)
    ).first()
    
    assert saved_request is not None
    assert saved_request.grade_level == "3a"
    assert saved_request.status == RequestStatus.OPEN
    assert saved_request.note == "Bring books"

def test_save_application_persists_teacher_and_request(db):
    admin = User(
        full_name="Admin",
        email="admin@test.com",
        password_hash="hashed",
        role=Role.ADMIN,
        personal_number="LP-2026-0003",
    )
    teacher = User(
        full_name="Teacher",
        email="teacher@test.com",
        password_hash="hashed",
        role=Role.TEACHER,
        personal_number="LP-2026-0004",
    )
    db.add(admin)
    db.add(teacher)
    db.commit()
    db.refresh(admin)
    db.refresh(teacher)

    subject = Subject(name="German", level="Primary", grades="1,2,3,4,5,6")
    db.add(subject)
    db.commit()
    db.refresh(subject)

    request = SubstituteRequest(
        created_by=admin.id,
        subject_id=subject.id,
        grade_level="4b",
        date=date(2026, 6, 1),
        status=RequestStatus.OPEN
    )
    db.add(request)
    db.commit()
    db.refresh(request)

    application = Application(
        teacher_id=teacher.id,
        request_id=request.id,
        status=ApplicationStatus.PENDING
    )
    db.add(application)
    db.commit()
    
    application = Application(
        teacher_id=teacher.id,
        request_id=request.id,
        status=ApplicationStatus.PENDING
    )
    db.add(application)
    db.commit()

    saved_application = db.exec(
        select(Application).where(Application.teacher_id == teacher.id)
    ).first()

    assert saved_application is not None
    assert saved_application.request_id == request.id
    assert saved_application.status == ApplicationStatus.PENDING