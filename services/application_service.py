from sqlmodel import Session, select
from models.application import Application, ApplicationStatus
from models.request import SubstituteRequest, RequestStatus

class ApplicationService:
    """All operations on Application objects."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def apply(self, teacher_id: int, request_id: int) -> dict:
        """Submit a teacher application for a request.
        Returns a dict with 'success' (bool) and 'message' (str).
        """
        # Check the request still exists and is OPEN
        req = self.db.exec(
            select(SubstituteRequest).where(SubstituteRequest.id == request_id)
        ).first()

        if not req:
            return {"success": False, "message": "Request not found."}
        if req.status != RequestStatus.OPEN:
            return {"success": False, "message": "This request already filled."}
        
        # Check if teacher already applied for this request
        if self.has_applied(teacher_id, request_id):
            return {"success": False, "message": "You already applied for this Request."}
        
        # Create the application
        appl = Application(teacher_id=teacher_id, request_id=request_id)
        self.db.add(appl)
        self.db.commit()
        self.db.refresh(appl)

        return {"success": True, "message": "Application submitted successfully!"}
    
    def has_applied(self, teacher_id: int, request_id: int) -> bool:
        """Check if a teacher has already applied for a specific request."""
        existing = self.db.exec(
            select(Application).where(
                Application.teacher_id == teacher_id,
                Application.request_id == request_id
            )
        ).first()
        return existing is not None
    
    def get_my_applications(self, teacher_id: int) -> list[Application]:
        """Return all application for a specific teacher."""
        return self.db.exec(
            select(Application).where(Application.teacher_id == teacher_id)
        ).all()
    