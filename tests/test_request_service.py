import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.user import User, Role
from models.request import SubstituteRequest, RequestStatus

from models.application import Application, ApplicationStatus
from services.request_service import RequestService
from datetime import date, datetime, timedelta, timezone

# --- Test database setup ---
@pytest.fixture
def db():
    """"Creates a fresh in memory SQLite DB for each test."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def admin_user(db):
    """"Creates a test admin user."""
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

@pytest.fixture
def service(db):
    return RequestService(db)

# --- Existing tests (fixed: removed school_name, updated grade values) ---
def test_create_request(db, admin_user, service):
    """"US-01: Admin can create a substitute request."""
    req = service.create_request(
        subject='Mathematics',
        grade_level='5a',
        date_obj=date(2026, 5, 10),
        note='Morning only.',
        admin_id=admin_user.id
    )
    assert req.id is not None
    assert req.subject == 'Mathematics'
    assert req.grade_level == '5a'
    assert req.status == RequestStatus.OPEN

def test_get_all_requests(db, admin_user, service):
    """US-03: admin can view all requests."""
    service.create_request(subject='Mathematics', grade_level='3a', date_obj=date(2026, 5, 1), note='', admin_id=admin_user.id)
    service.create_request(subject='German', grade_level='4b', date_obj=date(2026, 5, 2), note='', admin_id=admin_user.id)
    assert len(service.get_all_requests()) == 2


def test_get_open_requests(db, admin_user, service):
    """Only OPEN requests are returned by get_open_requests."""
    req = service.create_request(subject='Mathematics', grade_level='3a', date_obj=date(2026, 5, 1), note='', admin_id=admin_user.id)
    service.mark_filled(req.id)
    open_reqs = service.get_open_requests()
    assert len(open_reqs) == 0


def test_mark_filled(db, admin_user, service):
    """Request status changes to FILLED after mark_filled."""
    req = service.create_request(subject='Mathematics', grade_level='3a', date_obj=date(2026, 5, 1), note='', admin_id=admin_user.id)
    result = service.mark_filled(req.id)
    assert result is True
    updated = db.query(SubstituteRequest).filter_by(id=req.id).first()
    assert updated.status == RequestStatus.FILLED


def test_mark_filled_invalid_id(db, service):
    """mark_filled returns False for non-existent request."""
    assert service.mark_filled(9999) is False


def test_create_request_requires_all_fields(db, admin_user, service):
    """Request is stored with all provided fields correctly."""
    req = service.create_request(
        subject='History',
        grade_level='6a',
        date_obj=date(2026, 6, 15),
        note='Bring textbooks.',
        admin_id=admin_user.id
    )
    assert req.grade_level == '6a'
    assert req.note == 'Bring textbooks.'
    assert req.created_by == admin_user.id


# ── New tests (Member B) ──────────────────────────────────────────
def test_expired_request_is_deleted(db, admin_user, service):
    """A request whose expires_at is 13 hours ago must be deleted."""
    req = SubstituteRequest(
        created_by=admin_user.id,
        subject='German',
        grade_level='3a',
        date=date.today(),
        status=RequestStatus.OPEN,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=13),
    )
    db.add(req)
    db.commit()

    deleted = service.delete_expired_requests()

    assert deleted == 1
    assert db.query(SubstituteRequest).count() == 0


def test_valid_request_is_not_deleted(db, admin_user, service):
    """A request expiring in 2 hours must NOT be deleted."""
    req = SubstituteRequest(
        created_by=admin_user.id,
        subject='Mathematics',
        grade_level='2b',
        date=date.today(),
        status=RequestStatus.OPEN,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=2),
    )
    db.add(req)
    db.commit()

    deleted = service.delete_expired_requests()

    assert deleted == 0
    assert db.query(SubstituteRequest).count() == 1


def test_grade_filter_returns_kindergarten_only(db, admin_user, service):
    """get_requests_by_grade('KG') must return only KG1 / KG2 requests."""
    db.add(SubstituteRequest(
        created_by=admin_user.id, subject='Crafts',
        grade_level='KG1', date=date.today(), status=RequestStatus.OPEN
    ))
    db.add(SubstituteRequest(
        created_by=admin_user.id, subject='Mathematics',
        grade_level='3a', date=date.today(), status=RequestStatus.OPEN
    ))
    db.commit()

    result = service.get_requests_by_grade('KG')

    assert len(result) == 1
    assert result[0].grade_level == 'KG1'
