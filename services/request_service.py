from sqlalchemy.orm import Session
from datetime import date
from models.request import SubstituteRequest, RequestStatus
from models.application import Application, ApplicationStatus

class RequestService:

    def __init__(self, db: Session):
        self.db = db

    def create_request(self, school_name: str, subject: str,
                       grade_level: str, date_obj: date,
                       notes: str, admin_id: int) -> SubstituteRequest:
        
        req = SubstituteRequest(
            school_name=school_name,
            subject=subject,
            grade_level=grade_level,
            date=date_obj,
            note=notes,
            created_by=admin_id
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req
    
    def get_all_requests(self) -> list[SubstituteRequest]:
        return self.db.query(SubstituteRequest).order_by(
            SubstituteRequest.created_at.desc()
        ).all()
    
    def get_open_requests(self) -> list[SubstituteRequest]:
        return self.db.query(SubstituteRequest).filter(
            SubstituteRequest.status == RequestStatus.OPEN
        ).order_by(SubstituteRequest.created_at.desc()).all()
    
    def mark_filled(self, request_id: int) -> bool:
        req = self.db.query(SubstituteRequest).filter(
            SubstituteRequest.id == request_id
        ).first()
        if not req:
            return False
        req.status = RequestStatus.FILLED
        self.db.commit()
        return True
    

    def get_pending_applications(self) -> list[Application]:
        return self.db.query(Application).filter(
            Application.status == ApplicationStatus.PENDING
        ).order_by(Application.created_at.desc()).all()
    
    def approve_application(self, app_id: int) -> bool:
        application = self.db.query(Application).filter(
            Application.id == app_id
        ).first()
        if not application:
            return False
        application.status = ApplicationStatus.APPROVED
        self.mark_filled(application.request_id)
        self.db.commit()
        return True
    
    def reject_application(self, app_id: int) -> bool:
        application = self.db.query(Application).filter(
            Application.id == app_id
        ).first()
        if not application:
            return False
        application.status = ApplicationStatus.REJECTED
        self.db.commit()
        return True
    