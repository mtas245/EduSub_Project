import pytest
from datetime import date
from models import subject
from sqlmodel import SQLModel, Session, create_engine, select

from models.user import User, Role
from models.request import SubstituteRequest, RequestStatus
from models.application import Application, ApplicationStatus
from services.request_service import RequestService
from services.application_service import ApplicationService


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


def test_full_substitution_workflow(db):
    admin = User(
        full_name="Admin",
        email="admin@edusub.ch",
        password_hash="hashed",
        role=Role.ADMIN,
        personal_number="LP-2026-0100",
    )
    teacher = User(
        full_name="Jane Teacher",
        email="jane@edusub.ch",
        password_hash="hashed",
        role=Role.TEACHER,
        personal_number="LP-2026-0101",
    )

    db.add(admin)
    db.add(teacher)
    db.commit()
    db.refresh(admin)
    db.refresh(teacher)

    request_service = RequestService(db)
    application_service = ApplicationService(db)

    request = request_service.create_request(
        subject_id=subject.id,  # Replace with the actual subject ID
        grade_level="4a",
        date_obj=date(2026, 5, 20),
        note="Substitute needed",
        admin_id=admin.id,
        time_slot="08:00-10:00",
    )

    assert request.status == RequestStatus.OPEN

    result = application_service.apply(
        teacher_id=teacher.id,
        request_id=request.id,
    )

    assert result["success"] is True

    application = db.exec(
        select(Application).where(
            Application.teacher_id == teacher.id,
            Application.request_id == request.id,
        )
    ).first()

    assert application is not None
    assert application.status == ApplicationStatus.PENDING

    approved = request_service.approve_application(application.id)

    assert approved is True

    db.refresh(request)
    db.refresh(application)

    assert request.status == RequestStatus.FILLED
    assert application.status == ApplicationStatus.APPROVED


def test_duplicate_application_workflow_is_rejected(db):
    admin = User(
        full_name="Admin",
        email="admin2@edusub.ch",
        password_hash="hashed",
        role=Role.ADMIN,
        personal_number="LP-2026-0200",
    )
    teacher = User(
        full_name="John Teacher",
        email="john@edusub.ch",
        password_hash="hashed",
        role=Role.TEACHER,
        personal_number="LP-2026-0201",
    )

    db.add(admin)
    db.add(teacher)
    db.commit()
    db.refresh(admin)
    db.refresh(teacher)

    request_service = RequestService(db)
    application_service = ApplicationService(db)

    request = request_service.create_request(
        subject_id=subject.id,  # Replace with the actual subject ID
        grade_level="3a",
        date_obj=date(2026, 5, 21),
        note="",
        admin_id=admin.id,
    )

    first_result = application_service.apply(
        teacher_id=teacher.id,
        request_id=request.id,
    )

    second_result = application_service.apply(
        teacher_id=teacher.id,
        request_id=request.id,
    )

    assert first_result["success"] is True
    assert second_result["success"] is False
    assert "already applied" in second_result["message"].lower()