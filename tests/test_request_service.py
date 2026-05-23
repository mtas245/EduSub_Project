import pytest
from sqlmodel import create_engine, Session, SQLModel, select
from models.user import User, Role
from models.request import SubstituteRequest, RequestStatus
from models.subject import Subject
from models.application import Application, ApplicationStatus
from services.request_service import RequestService
from datetime import date, datetime, timedelta, timezone

# --- Fixtures ---

@pytest.fixture
def db():
    """Creates a fresh in-memory SQlite database for each test."""
    engine = create_engine('sqlite:///:memory:')
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def admin_user(db):
    """Creates and persists a test admin user."""
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
def teacher_user(db):
    """Creates a test teacher user."""
    user = User(
        id=2,
        email='teacher@test.com',
        password_hash='fakehash',
        full_name='Test Teacher',
        role=Role.TEACHER
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture
def subject_math(db):
    """Creates and persists a Mathematics subject."""
    s = Subject(name='Mathematics', level='Primary', grades='1,2,3,4,5,6')
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@pytest.fixture
def subject_german(db):
    """Creates and persists a German subject."""
    s = Subject(name='German', level='Primary', grades='1,2,3,4,5,6')
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@pytest.fixture
def subject_crafts(db):
    """Creates and persists a Crafts subject."""
    s = Subject(name='Crafts', level='Kindergarten', grades='KG1,KG2')
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@pytest.fixture
def service(db) -> RequestService:
    """Returns a RequestService instance bound to the test dastabase."""
    return RequestService(db)

@pytest.fixture
def sample_request(db, admin_user, subject_math, service) -> SubstituteRequest:
    """Creates a single open request for reuse across tests."""
    return service.create_request(
        subject_id=subject_math.id,
        grade_level='3a',
        date_obj=date(2026, 5, 10),
        note='',
        admin_id=admin_user.id,
    )

# --- Basic CRUD Tests ---

def test_create_request(sample_request: SubstituteRequest, subject_math: Subject):
    """US-01: Admin can create a substitute request with correct defaults."""
    assert sample_request.id is not None
    assert sample_request.subject_id == subject_math.id
    assert sample_request.grade_level == '3a'
    assert sample_request.status == RequestStatus.OPEN

def test_get_all_requests(db, admin_user, subject_math, service: RequestService):
    """US-03: Admin can view all substitute requests."""
    service.create_request(subject_id=subject_math.id, grade_level='3a', date_obj=date(2026, 5, 1), note='', admin_id=admin_user.id)
    service.create_request(subject_id=subject_math.id, grade_level='4b', date_obj=date(2026, 5, 2), note='', admin_id=admin_user.id)
    assert len(service.get_all_requests()) == 2

def test_get_openn_requests_excludes_filled(sample_request: SubstituteRequest, service: RequestService):
    """Only OPEN requests are returned after one is marked filled."""
    service.mark_filled(sample_request.id)
    assert len(service.get_open_requests()) == 0

def test_marked_filled(db, sample_request: SubstituteRequest, service: RequestService):
    """Request status changes to FILLED after mark_filled."""
    result = service.mark_filled(sample_request.id)
    assert result is True
    updated = service.db.get(SubstituteRequest, sample_request.id)
    assert updated.status == RequestStatus.FILLED

def test_mark_filled_nonexistent(service: RequestService):
    """mark_filled return False for a non-existent request ID."""
    assert service.mark_filled(9999) is False

def test_create_request_stores_all_fields(db, admin_user, subject_math, service: RequestService):
    """All fields are persisted correctly whem creating a request."""
    req = service.create_request(
        subject_id=subject_math.id,
        grade_level='6a',
        date_obj=date(2026, 6, 15),
        note='Bring textbooks',
        admin_id=admin_user.id,
    )
    assert req.grade_level == '6a'
    assert req.note == 'Bring textbooks'
    assert req.created_by == admin_user.id
    assert req.subject_id == subject_math.id

# --- Expiry Tests ---

def test_expired_request_is_deleted(db, admin_user, subject_german, service: RequestService):
    """A request whose expires_at is 13 hours ago must be deleted."""
    req = SubstituteRequest(
        created_by=admin_user.id,
        subject_id=subject_german.id,
        grade_level='3a',
        date=date.today(),
        status=RequestStatus.OPEN,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=13)
    )
    db.add(req)
    db.commit()

    deleted = service.delete_expired_requests()
    assert deleted == 1
    assert len(db.exec(select(SubstituteRequest)).all()) == 0

def test_valid_request_is_not_deleted(db, admin_user, subject_math, service: RequestService):
    """A request expiring in 2 hours must NOT be deleted."""
    req = SubstituteRequest(
        created_by=admin_user.id,
        subject_id=subject_math.id,
        grade_level='2b',
        date=date.today(),
        status=RequestStatus.OPEN,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=2)
    )
    db.add(req)
    db.commit()

    deleted = service.delete_expired_requests()
    assert deleted == 0
    assert len(db.exec(select(SubstituteRequest)).all()) == 1

# --- Parametrize: Grade Filter ---

@pytest.mark.parametrize("filter_level, expected_grade, expected_count", [
    ('KG', 'KG1', 1),
    ('KG', 'KG2', 1),
    ('Primary', '3a', 1),
])
def test_grade_filter_parametrized(db, admin_user, subject_crafts, subject_math,
                                   service: RequestService,
                                   filter_level: str, expected_grade: str,
                                   expected_count: int):
    """get_request_by_grade returns only the correct school level."""
    subject_id = subject_crafts.id if expected_grade in ('KG1', 'KG2') else subject_math.id
    db.add(SubstituteRequest(
        created_by=admin_user.id,
        subject_id=subject_id,
        grade_level=expected_grade,
        date=date.today(),
        status=RequestStatus.OPEN,
    ))
    db.commit()

    result = service.get_requests_by_grade(filter_level)
    assert len(result) == expected_count
    assert result[0].grade_level == expected_grade

def test_grade_filter_returns_kindergarten_only(db, admin_user, subject_crafts, subject_math,
                                                service: RequestService):
    """get_request_by_grade('KG') exclude primary school requests."""
    db.add(SubstituteRequest(
        created_by=admin_user.id,
        subject_id=subject_crafts.id,
        grade_level='KG1',
        date=date.today(),
        status=RequestStatus.OPEN,
    ))
    db.add(SubstituteRequest(
        created_by=admin_user.id,
        subject_id=subject_math.id,
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

# --- __repr__ and __str__ Tests---

def test_request_repr(sample_request: SubstituteRequest):
    """__repr__ contains key field for debugging."""
    r = repr(sample_request)
    assert '3a' in r
    assert 'open' in r

def test_request_str(sample_request: SubstituteRequest):
    """__str__ returns a user-friendly description."""
    s = str(sample_request)
    assert '3a' in s

# --- Applications Tests ---

def test_approve_application(db, admin_user, teacher_user, subject_german,
                             service: RequestService):
    """Approving an application sets status to APPROVED and request to FILLED."""
    req = service.create_request(
        subject_id=subject_german.id, grade_level='2a',
        date_obj=date(2026, 6, 1), note='', admin_id=admin_user.id
    )
    appl = Application(teacher_id=teacher_user.id, request_id=req.id)
    db.add(appl)
    db.commit()

    result = service.approve_application(appl.id)

    assert result is True
    db.refresh(appl)
    db.refresh(req)
    assert appl.status == ApplicationStatus.APPROVED
    assert req.status == RequestStatus.FILLED

def test_reject_application(db, admin_user, teacher_user, subject_math,
                            service: RequestService):
    """Rejecting an application sets status to REJECTED."""
    req = service.create_request(
        subject_id=subject_math.id, grade_level='4b',
        date_obj=date(2026, 6, 2), note='', admin_id=admin_user.id
    )
    appl = Application(teacher_id=teacher_user.id, request_id=req.id)
    db.add(appl)
    db.commit()

    result = service.reject_application(appl.id)

    assert result is True
    db.refresh(appl)
    assert appl.status == ApplicationStatus.REJECTED

def test_get_pending_application(db, admin_user, teacher_user, subject_math,
                                 service: RequestService):
    """get_pending_application returns only PENDING applications."""
    req = service.create_request(
        subject_id=subject_math.id, grade_level='1a',
        date_obj=date(2026, 6, 3), note='', admin_id=admin_user.id
    )
    appl = Application(teacher_id=teacher_user.id, request_id=req.id,
                       status=ApplicationStatus.PENDING)
    db.add(appl)
    db.commit()

    pending = service.get_pending_applications()
    assert len(pending) == 1

def test_get_approved_assignments_for_teacher(db, admin_user, teacher_user, subject_math,
                                              service: RequestService):
    """get_approved_assignments_for_teacher returns only approved requests."""
    req = service.create_request(
        subject_id=subject_math.id, grade_level='5a',
        date_obj=date(2026, 6, 4), note='', admin_id=admin_user.id
    )
    appl = Application(teacher_id=teacher_user.id, request_id=req.id,
                       status=ApplicationStatus.APPROVED)
    db.add(appl)
    db.commit()

    assignments = service.get_approved_assignments_for_teacher(teacher_user.id)

    assert len(assignments) == 1
    assert assignments[0].subject_id == subject_math.id
    
def test_calculate_expires_at_without_time_slot(service):
    """calculate_expires_at uses midnight minus 12h when no time_slot given."""
    from datetime import date, datetime
    result = service.calculate_expires_at(date(2026, 6, 1), time_slot=None)
    expected = datetime(2026, 5, 31, 12, 0)
    assert result == expected


def test_delete_expired_requests_handles_exception(db, admin_user, subject_math, service):
    """delete_expired_requests returns 0 on exception by using invalid state."""
    from unittest.mock import patch
    with patch.object(db, 'exec', side_effect=Exception('DB Error')):
        result = service.delete_expired_requests()
    assert result == 0


def test_approve_application_not_found(service):
    """approve_application returns False for unknown app_id."""
    assert service.approve_application(9999) is False

def test_reject_application_not_found(service):
    """reject_application returns False for unknown app_id."""
    assert service.reject_application(9999) is False

def test_calculate_expires_at_no_time_slot_direct(service):
    """Direct call to calculate_expires_at with time_slot=None hits else branch."""
    from datetime import date, datetime, time
    assignment_date = date(2026, 7, 1)
    result = service.calculate_expires_at(assignment_date, None)
    # Without time_slot, start_time = 00:00, so expires = day before at 12:00
    assert result == datetime(2026, 6, 30, 12, 0, 0)


            
    
    

