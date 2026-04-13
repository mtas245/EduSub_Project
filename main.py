from nicegui import ui, app
from database import engine, Base, SessionLocal
from models import user, request, application, subject
from models.subject import Subject, DEFAULT_SUBJECTS
from models.user import User
from models.request import SubstituteRequest, RequestStatus
from models.application import Application
from views.login import login_page
from views.register import register_page
from views.admin_dashboard import admin_dashboard

def require_login(allowed_roles: list[str]):
    """"
    Redirects to login if not authenticated or wrong role."""
    if not app.storage.user.get('logged_in'):
        ui.navigate.to('/')
        return False
    role = app.storage.user.get('role')
    if role not in allowed_roles:
        ui.navigate.to('/')
        return False
    return True

def seed_subjects():
    db = SessionLocal()
    try:
        if db.query(Subject).count() == 0:
            for s in DEFAULT_SUBJECTS:
                db.add(Subject(
                    name=s['name'],
                    level=s['level'],
                    grades=','.join(s['grades'])
                ))
            db.commit()
    finally:
        db.close()

@ui.page('/')
def index():
    login_page()

@ui.page('/register')
def register():
    register_page()

@ui.page('/logout')
def logout():
    app.storage.user.clear()
    ui.navigate.to('/')

@ui.page('/admin')
def admin():
    if not require_login(['admin']):
        return
    admin_dashboard()

@ui.page('/teacher')
def teacher():
    if not require_login(['teacher']):
        return
    ui.label('Teacher Dashboard - Coming Soon!')

if __name__ in {'__main__', '__mp_main__'}:
    Base.metadata.create_all(bind=engine)
    seed_subjects()
    ui.run(
        title='EduSub',
        storage_secret='EduSub-secret-key-changes-in-prod',
        port=8080,
        reload=False
    )