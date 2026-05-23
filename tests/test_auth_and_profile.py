import pytest
from sqlmodel import create_engine, Session, SQLModel, select
from models.user import User, Role
from models.subject import Subject, UserSubject
from services.profile_service import ProfileService
from auth import register_user, login_user, hash_password, verify_password, generate_personal_number

# --- Fixtures ---

@pytest.fixture
def db():
    """Create a fresh in memory sqlite database for each test."""
    engine = create_engine('sqlite:///:memory:')
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def teacher(db):
    """Creates a test teacher user."""
    user = User(
        email='teacher@test.com',
        password_hash=hash_password('secret123'),
        full_name='Jane Teacher',
        role=Role.TEACHER,
        phone='0791234567',
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def subject_math(db):
    s = Subject(name='Mathematics', level='Primary', grades='1,2,3,4,5,6')
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@pytest.fixture
def subject_pe(db):
    s = Subject(name='PE', level='Primary', grades='1,2,3,4,5,6')
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@pytest.fixture
def service(db) -> ProfileService:
    return ProfileService(db)

# --- Auth Tests ---

def test_hash_and_verify_password():
    """Hashed password can be verified with the original plain text."""
    plain = 'mypassword123'
    hashed = hash_password(plain)
    assert verify_password(plain, hashed)

def test_verify_wrong_password():
    """Wrong password does not verify."""
    hashed = hash_password('correct')
    assert not verify_password('wrong', hashed)

def test_register_user_success(db):
    """New user is created with correct fields and a personal number."""
    user = register_user(db, 'new@test.com', 'New User', 'pass1234',
                         'teacher', phone='0791111111')
    assert user is not None
    assert user.email == 'new@test.com'
    assert user.full_name == 'New User'
    assert user.role == Role.TEACHER
    assert user.phone == '0791111111'
    assert user.personal_number is not None
    assert user.personal_number.startswith('LP-2026-')

def test_register_user_duplicate_email(db):
    """Registering with an existing email returns None."""
    register_user(db, 'dup@test.com', 'First', 'pass1234', 'teacher')
    result = register_user(db, 'dup@test.com', 'Second', 'pass1234', 'teacher')
    assert result is None

def test_register_user_with_documents_path(db):
    """documents_path is saved correctly."""
    user = register_user(db, 'doc@test.com', 'Doc User', 'pass1234', 'teacher',
                         documents_path='uploads/documents/cert.pdf')
    assert user.documents_path == 'uploads/documents/cert.pdf'

def test_login_user_success(db):
    """Correct credentials return the user."""
    register_user(db, 'login@test.com', 'Login User', 'mypassword', 'admin')
    user = login_user(db, 'login@test.com', 'mypassword')
    assert user is not None
    assert user.email == 'login@test.com'

def test_login_user_wrong_password(db):
    """Wrong password returns None."""
    register_user(db, 'wp@test.com', 'WP User', 'correct', 'teacher')
    result = login_user(db, 'wp@test.com', 'wrong')
    assert result is None

def test_login_user_not_found(db):
    """None-existent email returns None."""
    result = login_user(db, 'nobody@test.com', 'pass')
    assert result is None

def test_generate_personal_number_unique(db):
    """Generated personal numbers are unique."""
    nums = {generate_personal_number(db) for _ in range(10)}
    assert len(nums) == 10

# --- ProfilService Tests ---

def test_get_profile(db, teacher, service):
    """get_profile returns the correct user."""
    user = service.get_profile(teacher.id)
    assert user is not None
    assert user.email == 'teacher@test.com'

def test_get_profile_not_found(db, service):
    """get_profile returns None for unknown user."""
    assert service.get_profile(9999) is None

def test_update_profile_name_and_phone(db, teacher, service):
    """update_profile saves full_name and phone correctly."""
    updated = service.update_profile(teacher.id, full_name='Updated Name',
                                     phone='0799999999')
    assert updated.full_name == 'Updated Name'
    assert updated.phone == '0799999999'

def test_update_profile_bio(db, teacher, service):
    """update_profile saves bio correctly."""
    updated = service.update_profile(teacher.id, bio='Experienced substitute teacher.')
    assert updated.bio == 'Experienced substitute teacher.'

def test_update_profile_ignores_email(db, teacher, service):
    """update_profile does not change email even if passed."""
    service.update_profile(teacher.id, email='hacked@test.com')
    user = service.get_profile(teacher.id)
    assert user.email == 'teacher@test.com'

def test_update_profile_not_found(db, service):
    """update_profile returns None for unknown user."""
    result = service.update_profile(9999, full_name='Ghost')
    assert result is None

def test_get_subjects_empty(db, teacher, service):
    """get_subject returns empty list when no subjects assigned."""
    result = service.get_subjects(teacher.id)
    assert result == []

def test_set_and_get_subjects(db, teacher, subject_math, subject_pe, service):
    """set_subjects saves and get_subjects retrieves correctly."""
    service.set_subjects(teacher.id, [subject_math.id, subject_pe.id])
    subjects = service.get_subjects(teacher.id)
    names = {s.name for s in subjects}
    assert names == {'Mathematics', 'PE'}

def test_set_subjects_replaces_existing(db, teacher, subject_math, subject_pe, service):
    """set_subjects replaces previous assignments."""
    service.set_subjects(teacher.id, [subject_math.id, subject_pe.id])
    service.set_subjects(teacher.id, [subject_math.id])
    subjects = service.get_subjects(teacher.id)
    assert len(subjects) == 1
    assert subjects[0].name == 'Mathematics'

def test_set_subjects_empty_clears_all(db, teacher, subject_math, service):
    """set_subjects with empty list removes all assignments."""
    service.set_subjects(teacher.id, [subject_math.id])
    service.set_subjects(teacher.id, [])
    assert service.get_subjects(teacher.id) == []

def test_get_pending_teachers(db):
    """get_pending_teachers returns only unapproved teachers."""
    teacher = User(email='pending@test.com', password_hash='x',
                   full_name='Pending', role=Role.TEACHER,
                   personal_number='LP-2026-9001', is_approved=False)
    db.add(teacher)
    db.commit()
    service = ProfileService(db)
    pending = service.get_pending_teachers()
    assert len(pending) >= 1
    assert all(not u.is_approved for u in pending)

def test_approve_teacher_not_found(db):
    """approve_teacher returns False for unknown user."""
    service = ProfileService(db)
    assert service.approve_teacher(9999) is False

def test_approve_teacher_wrong_role(db):
    """approve_teacher returns False if user is not a teacher."""
    admin = User(email='admin99@test.com', password_hash='x',
                 full_name='Admin', role=Role.ADMIN,
                 personal_number='LP-2026-9002', is_approved=True)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    service = ProfileService(db)
    assert service.approve_teacher(admin.id) is False

def test_reject_teacher_not_found(db):
    """reject_teacher returns False for unknown user."""
    service = ProfileService(db)
    assert service.reject_teacher(9999) is False


def test_reject_teacher_wrong_role(db):
    """reject_teacher returns False if user is not a teacher."""
    admin = User(email='admin100@test.com', password_hash='x',
                 full_name='Admin2', role=Role.ADMIN,
                 personal_number='LP-2026-9003', is_approved=True)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    service = ProfileService(db)
    assert service.reject_teacher(admin.id) is False

def test_approve_teacher_success(db):
    """approve_teacher sets is_approved to True for a teacher."""
    teacher = User(email='approve@test.com', password_hash='x',
                   full_name='To Approve', role=Role.TEACHER,
                   personal_number='LP-2026-9004', is_approved=False)
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    service = ProfileService(db)
    result = service.approve_teacher(teacher.id)
    assert result is True
    db.refresh(teacher)
    assert teacher.is_approved is True


def test_reject_teacher_success(db):
    """reject_teacher deletes the teacher account."""
    teacher = User(email='reject@test.com', password_hash='x',
                   full_name='To Reject', role=Role.TEACHER,
                   personal_number='LP-2026-9005', is_approved=False)
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    tid = teacher.id
    service = ProfileService(db)
    result = service.reject_teacher(tid)
    assert result is True
    assert db.get(User, tid) is None

def test_login_user_not_approved(db):
    """Teacher not approved returns None on login."""
    register_user(db, 'notapproved@test.com', 'Not Approved', 'pass123', 'teacher')
    result = login_user(db, 'notapproved@test.com', 'pass123')
    assert result is None