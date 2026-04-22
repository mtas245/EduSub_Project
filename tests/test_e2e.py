import pytest
from sqlmodel import create_engine, Session, SQLModel, select
from datetime import date
from models.user import User, Role
from models.request import SubstituteRequest, RequestStatus
from models.application import Application, ApplicationStatus
from services.application_service import ApplicationService
from services.request_service import RequestService

@pytest.fixture
def db():
    """Creates a fresh in-memory SQLite database for the E2E test."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()

def test_full_substitution_workflow(db):
    """
    Full E2E workflow:
    1. Admin creates a substitute request (Grade 4a, French)
    2. Teacher applies for the request
    3. Admin approves the application
    4. Request status -> FILLED, Application status -> APPROVED
    """
    # --- Setup: Admin and Teacher ---
    admin = User(
        full_name='Admin',
        email='admin@edusub.ch',
        password_hash='x',
        role=Role.ADMIN,
        personal_number='LP-2026-0001'
    )
    teacher = User(
        full_name='Jane Teacher', email='jane@edusub.ch',
        password_hash='x', role=Role.TEACHER,
        personal_number='LP-2026-0042')
    
    db.add_all([admin, teacher])
    db.commit()

    req_svc = RequestService(db)
    app_svc = ApplicationService(db)

    #--- Step 1: Admin creates a request---
    request = req_svc.create_request(
        subject='French',
        grade_level='4a',
        date_obj=date(2026, 5, 20),
        note='',
        admin_id=admin.id
    )
    assert request.status == RequestStatus.OPEN

    #--- Step 2: Teacher applies---
    result = app_svc.apply(
        teacher_id=teacher.id,
        request_id=request.id
    )
    assert result['success'] is True

    application = db.exec(
        select(Application).where(
            Application.teacher_id == teacher.id,
            Application.request_id == request.id
        )
    ).first()
    assert application is not None
    assert application.status == ApplicationStatus.PENDING

    #---- Step 3: Admin approves---
    approved = req_svc.approve_application(application.id)
    assert approved is True

    #--- Step 4: Verify final result---
    db.refresh(request)
    db.refresh(application)
    assert request.status == RequestStatus.FILLED
    assert application.status == ApplicationStatus.APPROVED

def test_duplicate_application_is_rejected(db):
    """A teacher cannot apply twice for the same rewquest."""
    admin = User(full_name='Admin', email='admin2@edusub.ch',
                 password_hash='x', role=Role.ADMIN,
                 personal_number='LP-2026-0002')
    teacher = User(full_name='John Teacher', email='john@edusub.ch',
                   password_hash='x', role=Role.TEACHER,
                   personal_number='LP-2026-0043')
    db.add_all([admin, teacher])
    db.commit()

    req_svc = RequestService(db)
    app_svc = ApplicationService(db)

    request = req_svc.create_request(
        subject='Math', grade_level='3a',
        date_obj=date(2026, 5, 21), note='', admin_id=admin.id
    )

    # First application - should succeed
    result1 = app_svc.apply(teacher_id=teacher.id, request_id=request.id)
    assert result1['success'] is True

    # Second application shoul be rejeected
    result2 = app_svc.apply(teacher_id=teacher.id, request_id=request.id)
    assert result2['success'] is False
    assert 'already applied' in result2['message'].lower()
