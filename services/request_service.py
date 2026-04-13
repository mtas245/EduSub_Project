from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta, time as dt_time, timezone
from models.request import SubstituteRequest, RequestStatus
from models.application import Application, ApplicationStatus


class RequestService:

    def __init__(self, db: Session):
        self.db = db

    def create_request(self, subject: str, grade_level: str,
                       date_obj: date, note: str,
                       admin_id: int) -> SubstituteRequest:
        req = SubstituteRequest(
            subject=subject,
            grade_level=grade_level,
            date=date_obj,
            note=note,
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

    def get_requests_by_grade(self, level: str) -> list[SubstituteRequest]:
        all_open = self.get_open_requests()
        if level == 'KG':
            return [r for r in all_open
                    if r.grade_level in ('KG1', 'KG2')]
        elif level == 'Primary':
            return [r for r in all_open
                    if r.grade_level not in ('KG1', 'KG2')]
        return all_open

    def calculate_expires_at(self, assignment_date: date,
                              time_slot: str = None) -> datetime:
        if time_slot:
            start_str    = time_slot.split('-')[0].strip()
            hour, minute = map(int, start_str.split(':'))
            start_time   = dt_time(hour, minute)
        else:
            start_time = dt_time(0, 0)
        assignment_dt = datetime.combine(assignment_date, start_time)
        return assignment_dt - timedelta(hours=12)

    def delete_expired_requests(self) -> int:
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            expired = self.db.query(SubstituteRequest).filter(
                SubstituteRequest.status     == RequestStatus.OPEN,
                SubstituteRequest.expires_at != None,
                SubstituteRequest.expires_at  < now
            ).all()
            count = len(expired)
            for req in expired:
                self.db.delete(req)
            self.db.commit()
            return count
        except Exception:
            return 0

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
        ).all()

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
    