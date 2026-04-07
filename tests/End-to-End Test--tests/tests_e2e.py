# tests/test-e2e.py
import pytest
from sqlalchemy import crate_engine
from sqlalchemy.orm import sessionmaker
from datatime import Date
from database import Base
from models.user import User
from models.request import SubstituteRequest
from models.application import Application
from services.application_service import ApplicationService
from services.request_service import RequestService


@pytest.fixture
def db():
    engine = crate_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine) ()
    yield session
    session.close()

    def test_full_substitution_workflow(db):
        """
        1. Admin creates a request (Grade 4a, French)
        2. Teacher applies
        3. Admin approves
        4. Request status -> FILLED, Application status -> APPROVED
        """
        admin = User(full_name='Admin', email='admin@edusub.ch'
        password_hash='x', role='Admin',
        personal_numbers='LP-2026-0001')
        teacher = User(full_name='Jane Teacher', email='jane@edusub.ch',
                       password_hash='x', role='Teacher',
                       personal_number='LP-2026-0042')
        db.add_all([admin, teacher])
        db.commit()

        req_svc = RequestService(db)
        app_svc = ApplicationService(db)

        # Grade 4a -> French is available
        request = req_svc.crate_request(
            created_by=admin.id, subject='French',
            grade_level='4a', date=date(2026, 5, 20)
        )
        assert request.status == 'OPEN'

        application = app_svc.crate_application(
            teacher_id=teacher.id, request_id=request.id
        )
        assert application.status == 'PENDING'

        app_svc.approve_applicatiob(application.id)


        db.refresh(request)
        db.refresh(application)
        assert request.status == 'FILLED'
        assert application.status == 'APPROVED'



