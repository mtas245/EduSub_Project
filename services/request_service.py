from sqlmodel import Session, select
from datetime import date, datetime, timedelta, time as dt_time, timezone
from models.request import SubstituteRequest, RequestStatus
from models.application import Application, ApplicationStatus


class RequestService:

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_request(
            self,
            subject: str,
            grade_level: str,
            date_obj: date,
            note: str,
            admin_id: int,
            time_slot: str | None = None
    ) -> SubstituteRequest:
        """Create a new substitute request and calculate its expiry time."""
        req = SubstituteRequest(
            subject=subject,
            grade_level=grade_level,
            date=date_obj,
            note=note,
            created_by=admin_id,
            time_slot=time_slot
        )
        req.expires_at = self.calculate_expires_at(date_obj, time_slot)  # Fix 2: calculate_expiry → calculate_expires_at
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def get_all_requests(self) -> list[SubstituteRequest]:
        return self.db.exec(
            select(SubstituteRequest).order_by(SubstituteRequest.created_at.desc())
        ).all()

    def get_open_requests(self) -> list[SubstituteRequest]:
        return self.db.exec(
            select(SubstituteRequest)
            .where(SubstituteRequest.status == RequestStatus.OPEN)
            .order_by(SubstituteRequest.created_at.desc())
        ).all()

    def get_requests_by_grade(self, level: str) -> list[SubstituteRequest]:  # Fix 5: Einrückung korrigiert
        all_open = self.get_open_requests()
        if level == 'KG':
            return [r for r in all_open if r.grade_level in ('KG1', 'KG2')]
        elif level == 'Primary':
            return [r for r in all_open if r.grade_level not in ('KG1', 'KG2')]
        return all_open

    def calculate_expires_at(self, assignment_date: date, time_slot: str | None = None) -> datetime:
        """Calculate the expiry time for a request: 12 hours before the assignment starts."""
        if time_slot:
            start_str = time_slot.split('-')[0].strip()
            hour, minute = map(int, start_str.split(':'))
            start_time = dt_time(hour, minute)
        else:
            start_time = dt_time(0, 0)
        assignment_dt = datetime.combine(assignment_date, start_time)  # Fix 3: assignment_datetime → assignment_dt
        return assignment_dt - timedelta(hours=12)

    def delete_expired_requests(self) -> int:
        """Delete all OPEN requests that have passed their expiry time."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        try:
            expired = self.db.exec(
                select(SubstituteRequest)
                .where(
                    SubstituteRequest.status == RequestStatus.OPEN,
                    SubstituteRequest.expires_at != None,
                    SubstituteRequest.expires_at < now
                )
            ).all()
            count = len(expired)  # Fix 4: count vor der Schleife definiert
            for req in expired:
                self.db.delete(req)
            self.db.commit()
            return count
        except Exception:
            self.db.rollback()
            return 0

    def mark_filled(self, request_id: int) -> bool:
        """Mark a request as filled. Returns True if successful."""
        req = self.db.get(SubstituteRequest, request_id)
        if not req:
            return False
        req.status = RequestStatus.FILLED
        self.db.commit()
        return True

    def get_pending_applications(self) -> list[Application]:
        return self.db.exec(
            select(Application).where(Application.status == ApplicationStatus.PENDING)
        ).all()

    def approve_application(self, app_id: int) -> bool:
        """Approve an application and mark the associated request as filled. Returns True if successful."""
        application = self.db.get(Application, app_id)
        if not application:
            return False
        application.status = ApplicationStatus.APPROVED
        self.mark_filled(application.request_id)
        self.db.commit()
        return True

    def reject_application(self, app_id: int) -> bool:
        application = self.db.get(Application, app_id)
        if not application:
            return False
        application.status = ApplicationStatus.REJECTED
        self.db.commit()
        return True

    def get_approved_assignments_for_teacher(self, teacher_id: int) -> list[SubstituteRequest]:
        return self.db.exec(
            select(SubstituteRequest)
            .join(Application, SubstituteRequest.id == Application.request_id)
            .where(
                Application.teacher_id == teacher_id,
                Application.status == ApplicationStatus.APPROVED
            )
            .order_by(SubstituteRequest.date.asc())
        ).all()
