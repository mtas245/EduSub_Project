from datetime import date
from auth import hash_password, verify_password
from models.request import RequestStatus, GRADE_LEVELS
from models.user import Role, User
from models.subject import Subject


def test_password_hashing_and_verification():
    password = "Password@123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True


def test_wrong_password_fails_verification():
    password = "Password@123"
    wrong_password = "WrongPassword123"
    hashed = hash_password(password)
    assert verify_password(wrong_password, hashed) is False


def test_request_status_enum_values():
    assert RequestStatus.OPEN.value == "open"
    assert RequestStatus.FILLED.value == "filled"
    assert RequestStatus.CANCELLED.value == "cancelled"


def test_role_enum_values():
    assert Role.ADMIN.value == "admin"
    assert Role.TEACHER.value == "teacher"


def test_grade_levels_contains_kindergarten_and_primary_levels():
    assert "KG1" in GRADE_LEVELS
    assert "KG2" in GRADE_LEVELS
    assert "3a" in GRADE_LEVELS
    assert "6b" in GRADE_LEVELS


def test_subject_repr():
    """Subject __repr__ returns expected string."""
    s = Subject(name='German', level='Primary')
    assert repr(s) == '<Subject German (Primary)>'


def test_user_repr():
    """User __repr__ returns expected string."""
    u = User(email='test@test.com', password_hash='x',
             full_name='Test', role=Role.TEACHER)
    assert repr(u) == '<User test@test.com (Role.TEACHER)>'