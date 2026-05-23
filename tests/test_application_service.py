import pytest
from sqlmodel import create_engine, Session, SQLModel
from datetime import date
from models.user import User, Role
from models.request import SubstituteRequest, RequestStatus
from models.subject import Subject
from models.application import Application, ApplicationStatus
from services.application_service import ApplicationService
from services.request_service import RequestService


@pytest.fixture
def db():
    engine = create_engine('sqlite:///:memory:')
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def admin(db):
    user = User(email='admin@test.com', password_hash='x',
                full_name='Admin', role=Role.ADMIN, personal_number='LP-2026-0001')
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def teacher(db):
    user = User(email='teacher@test.com', password_hash='x',
                full_name='Teacher', role=Role.TEACHER, personal_number='LP-2026-0002')
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def subject(db):
    s = Subject(name='German', level='Primary', grades='1,2,3,4,5,6')
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@pytest.fixture
def open_request(db, admin, subject):
    req = SubstituteRequest(
        created_by=admin.id, subject_id=subject.id,
        grade_level='3a', date=date(2026, 6, 1), status=RequestStatus.OPEN
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@pytest.fixture
def service(db):
    return ApplicationService(db)


def test_apply_request_not_found(db, teacher, service):
    """apply() returns failure when request does not exist."""
    result = service.apply(teacher_id=teacher.id, request_id=9999)
    assert result['success'] is False
    assert 'not found' in result['message'].lower()


def test_apply_request_already_filled(db, admin, teacher, subject, service):
    """apply() returns failure when request is already FILLED."""
    req = SubstituteRequest(
        created_by=admin.id, subject_id=subject.id,
        grade_level='3a', date=date(2026, 6, 2), status=RequestStatus.FILLED
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    result = service.apply(teacher_id=teacher.id, request_id=req.id)
    assert result['success'] is False
    assert 'filled' in result['message'].lower()


def test_get_my_applications(db, teacher, open_request, service):
    """get_my_applications returns all applications for a teacher."""
    service.apply(teacher_id=teacher.id, request_id=open_request.id)
    apps = service.get_my_applications(teacher.id)
    assert len(apps) == 1
    assert apps[0].teacher_id == teacher.id


def test_get_my_applications_empty(db, teacher, service):
    """get_my_applications returns empty list when no applications."""
    apps = service.get_my_applications(teacher.id)
    assert apps == []