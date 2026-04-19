from nicegui import ui, app
from database import engine, SessionLocal, create_db
from models import User, SubstituteRequest, Application, Subject
from models.subject import DEFAULT_SUBJECTS
from models.request import RequestStatus
from models.application import ApplicationStatus
from views.login import login_page
from views.register import register_page
from views.admin_dashboard import admin_dashboard
from views.teacher_dashboard import teacher_dashboard_view
from views.profile import profile_view

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
    from sqlmodel import Session, select
    with Session(engine) as session:
        if session.exec(select(Subject)).first() is None:
            for s in DEFAULT_SUBJECTS:
                session.add(Subject(
                    name=s['name'],
                    level=s['level'],
                    grades=','.join(s['grades'])
                ))
            session.commit()


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
    teacher_dashboard_view()

@ui.page('/profile')
def profile():
    if not require_login(['teacher', 'admin']):
        return
    profile_view()

@ui.page('/admin/teacher/{teacher_id}')
def admin_teacher_profile(teacher_id: int):
    if not require_login(['admin']):
        return
    from views.admin_teacher_profile import admin_teacher_profile_view
    admin_teacher_profile_view(teacher_id)

if __name__ in {'__main__', '__mp_main__'}:
    create_db()
    seed_subjects()
    ui.run(
        title='EduSub',
        storage_secret='EduSub-secret-key-change-in-prod',
        port=8080,
        reload=False
    )
