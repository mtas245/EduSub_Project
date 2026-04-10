import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.user import User, Role
from models.request import SubstituteRequest, RequestStatus
from services.request_service import RequestService
from datetime import date

# -- Test database setup --
@pytest.fixture
def db():
    """Creates a fresh in-memory SQLite DB for each test."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def admin_user(db):
    """Creates a test admin user."""
    user = User(
        id=1,
        email='admin@test.com',
        password_hash='fakehash',
        full_name='Test Admin',
        role=Role.ADMIN
    )
    db.add(user)
    db.commit()
    return user

# -- Tests --
def test_create_request(db, admin_user):
    """US-01: admin can create a substitute request."""
    svc = RequestService(db)
    req = svc.create_request(
        school_name='Schule Basel',
        subject='Mathematics',
        grade_level='5th',
        date_obj=date(2026, 5, 10),
        notes='Morning only.',
        admin_id=admin_user.id
    )
    assert req.id is not None
    assert req.school_name == 'Schule Basel'
    assert req.subject == 'Mathematics'
    assert req.status == RequestStatus.OPEN

def test_get_all_requests(db, admin_user):
    """"US-03: admin can view all requests."""
    svc = RequestService(db)
    svc.create_request('School A', 'Math', '3rd', date(2026, 5, 1), '', admin_user.id)
    svc.create_request('School B', 'Science', '4th', date(2026, 5, 2), '', admin_user.id)
    all_requests = svc.get_all_requests()
    assert len(all_requests) == 2

def test_get_open_requests(db, admin_user):
    """"Only OPEN requests are returned by get_open_requests."""
    svc = RequestService(db)
    req = svc.create_request('School A', 'Math', '3rd', date(2026, 5, 1), '', admin_user.id)
    result = svc.mark_filled(req.id)
    assert result is True
    updated_req = db.query(SubstituteRequest).filter_by(id=req.id).first()
    assert updated_req.status == RequestStatus.FILLED

def test_mark_filled(db, admin_user):
    """"Request status changes to FILLED after mark_filled."""
    svc = RequestService(db)
    req = svc.create_request('School A', 'Math', '3rd', date(2026, 5, 1), '', admin_user.id)
    result = svc.mark_filled(req.id)
    assert result is True
    updated_req = db.query(SubstituteRequest).filter_by(id=req.id).first()
    assert updated_req.status == RequestStatus.FILLED

def test_mark_filled_invalid_id(db):
    """"mark_filled return False for non_existent request. """
    svc = RequestService(db)
    result = svc.mark_filled(9999)  # Assuming 9999 is a non-existent ID
    assert result is False

def test_create_request_requires_all_fields(db, admin_user):
    """"Request is stored with all provided fields correctly."""
    svc = RequestService(db)
    req = svc.create_request(
        school_name='Schule Basel',
        subject='History',
        grade_level='6th',
        date_obj=date(2026, 6, 15),
        notes='Bring textbooks.',
        admin_id=admin_user.id
    )
    assert req.grade_level == '6th'
    assert req.note == 'Bring textbooks.'
    assert req.created_by == admin_user.id

    

