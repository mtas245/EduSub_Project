import pytest
from sqlalchemy import create_engnine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.user import User, Role
from models.request import SubstituteRequest, RequestStatus
from models.application import Application, ApplicationStatus
from services.request_service import RequestService
from datetime import date, datetime, timedelta, timezone

# --- Fixtures ---

@pytest.fixture
def db():
    """"Creates a fresh in-memory SQLite database for each test."""
    engine = create_engnine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def admin_user(db):
    """"Creates and persists a test admin user."""
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
def service(db) -> RequestService:
    """""Returns a RequestService instance bound to the test database."""
    return RequestService(db)

@pytest.fixture
def sample_request(db, admin_user, service) -> SubstituteRequest:
    """""Creates a single open request for reuse across tests."""
    return service.create_request(
        subject='Mathematics',
        grade_level='3a',
        date_obj=date(2026, 5, 10),
        note='',
        admin_id=admin_user.id,
    )

# --- Basic CRUD Tests ---

def test_create_request(sample_request: SubstituteRequest):
    """US-01: Admin can create a substitute request with correct defaults."""
    assert sample_request.id is not None
    assert sample_request.subject == 'Mathematics'
    assert sample_request.grade_level == '3a'
    assert sample_request.status == RequestStatus.OPEN

def test_get_all_requests(db, admin_user, service: RequestService):
    """"US.03 Admin can view all substitute requests."""
    service.create_request(subject='Mathematics', grade_level='3a', date_obj=date(2026, 5, 1), note='', admin_id=admin_user.id)
    service.create_request(subject='Science', grade_level='4b', date_obj=date(2026, 5, 2), note='', admin_id=admin_user.id)
    assert len(service.get_all_requests()) == 2

def test_get_open_requests_excludes_filled(sample_request: SubstituteRequest,
                                           service: RequestService):
    """""Only OPEN requests are returned after one is marked filled."""
    service.mark_filled(sample_request.id)
    assert len(service.get_open_requests()) == 0

def test_marked_filled(db, sample_request: SubstituteRequest, service: RequestService):
    """Request status changes to FILLED after mark_filled."""
    result = service.mark_filled(sample_request.id)
    assert result is True
    updated = service.db.get(SubstituteRequest, sample_request.id)
    assert updated.status == RequestStatus.FILLED

def test_mark_filled_nonexistent(service: RequestService):
    """"mark_filled returns False for a non-existent request ID."""
    assert service.mark_filled(9999) is False

def test_create_request_stores_all_fields(db, admin_user, service: RequestService):
    """"All fiields are persisted correctly when creating a request."""
    req = service.create_request(
        subject='History',
        grade_level='6a',
        date_obj=date(2026, 6, 15),
        note='Bring textbooks',
        admin_id=admin_user.id,
    )
    assert req.grade_level == '6a'
    assert req.note == 'Bring textbooks'
    assert req.created_by == admin_user.id

# --- Expiry Tests ---

def test_expired_request_is_deleted(db, admin_user, service: RequestService):
    """""A request whose expires_at is 13 hours ago must be deleted."""
    req = SubstituteRequest(
        created_by=admin_user.id,
        subject='German',
        grade_level='3a',
        date=date.today(),
        status=RequestStatus.OPEN,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=13)
    )
    db.add(req)
    db.commit()

    deleted = service.delete_expired_requests()
    assert deleted == 1
    assert db.query(SubstituteRequest).count() == 0

def test_valid_request_is_not_deleted(db, admin_user, service: RequestService):
    """A request expiring in 2 hours must NOT be deleted."""
    req= SubstituteRequest(
        created_by=admin_user.id,
        subject='Mathematics',
        grade_level='2b',
        date=date.today(),
        status=RequestStatus.OPEN,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=2)
    )
    db.add(req)
    db.commit()

    deleted = service.delete_expired_requests()

    assert deleted == 0
    assert db.query(SubstituteRequest).count() == 1

# --- Parameterize: Grade Filter ---

@pytest.mark.parametrize("filter_level, expected_grade, expected_count", [
    ('KG', 'KG1', 1),
    ('KG', 'KG2', 1),
    ('Primary', '3a', 1),
])
def test_grade_filter_parametrized(db, admin_user, service: RequestService,
                                   filter_level: str, expected_grade: str,
                                   expected_count: int):
    """get_reguests_by_grade returns only the correct school level."""
    db.add(SubstituteRequest(
        created_by=admin_user.id,
        subject='Crafts',
        grade_level=expected_grade,
        date=date.today(),
        status=RequestStatus.OPEN,
    ))
    db.commit()

    result = service.get_requests_by_grade(filter_level)

    assert len(result) == expected_count
    assert result[0].grade_level == expected_grade

def test_grade_filter_returns_kindergarten_only(db, admin_user, service: RequestService):
    """get_requests_by_grade('KG') exludes primary school requests"""
    db.add(SubstituteRequest(
        created_by=admin_user.id,
        subject='Crafts',
        grade_level='KG1',
        date=date.today(),
        status=RequestStatus.OPEN,
    ))
    db.add(SubstituteRequest(
        created_by=admin_user.id,
        subject='Mathematics',
        grade_level='3a',
        date=date.today(),
        status=RequestStatus.OPEN,
    ))
    db.commit()

    result = service.get_requests_by_grade('KG')

    assert len(result) == 1
    assert result[0].grade_level == 'KG1'

# --- Parametrize: RequestStatus Enum ---

@pytest.mark.parametrize("status", [
    RequestStatus.OPEN,
    RequestStatus.FILLED,
    RequestStatus.CANCELLED,
])
def test_request_status_enum_values(status: RequestStatus):
    """All RequestStatus enum values are valid strings."""
    assert isinstance(status.value, str)
    assert status.value in ('open', 'filled', 'cancelled')

# --- __repr__ and __str__ Tests ---

def test_request_repr(sample_request: SubstituteRequest):
    """__repr__ contains key fields for debugging."""
    r = repr(sample_request)
    assert 'Mathematics' in r
    assert '3a' in r
    assert 'open' in r

def test_request_str(sample_request: SubstituteRequest):
    """__str__ returns a user-friendly description."""
    s = str(sample_request)
    assert 'Mathematics' in s
    assert '3a' in s
    
