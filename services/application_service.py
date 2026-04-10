from typing import List
from sqlalchemy.orm import Session
from models.application import Application, ApplicationStatus
from models.request import SubstituteRequest, RequestStatus


class ApplicationService:
    """All Operations on Application objects"""

    def __init__(self, db: Session):
        self.db = db

    def apply(self, teacher_id: int, request_id: int) -> dict:
        """
        Submit a teacher application for a request.
        Returns a dict with 'success' (bool) and 'message' (str).
        """
        # Check the requests still exists and is OPEN
        req = (
            self.db.query(SubstituteRequest)
            .filter(SubstituteRequest.id == request_id)
            .first()
        )

        if not req:
            return {"success": False, "message": "Request not found"}
        if req.status != RequestStatus.OPEN:
            return {"success": False, "message": "This request is already filled."}

        # Check if teacher already applied for this request
        existing = (
            self.db.query(Application)
            .filter(
                Application.teacher_id == teacher_id,
                Application.request_id == request_id,
            )
            .first()
        )

        if existing:
            return {
                "success": False,
                "message": "You already applied for this request.",
            }

        # Create the Application
        appl = Application(teacher_id=teacher_id, request_id=request_id)
        self.db.add(appl)
        self.db.commit()
        self.db.refresh(appl)

        return {"success": True, "message": "Application submitted successfully!"}

    def get_my_applications(self, teacher_id: int) -> List[Application]:
        """Return all applications for a specific teacher."""
        return (
            self.db.query(Application)
            .filter(Application.teacher_id == teacher_id)
            .all()
        )
