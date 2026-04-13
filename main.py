from nicegui import ui, app
from database import engine, Base, SessionLocal
from edumatch.models.subject import DEFAULT_SUBJECTS
from views.admin_dashboard import admin_dashboard
from models.user import User
from models.request import SubstituteRequest, RequestStatus
from models.application import Application
from views.login import login_page
from views.register import register_page
from models import user, request, application, subject
from models.subject import Subject, DEFAULT_SUBJECTS



from views.login import login_page
from views.register import register_page

def require_login(allowed_roles: list[str]):
    '''
    Call at the top of any protected page.
    Redirects to login if not authenticated or wrong role.
    '''
    if not app.storage.user.get('logged_in'):
        ui.navigate.to('/')
        return False
    role = app.storage.user.get('role')
    if role not in allowed_roles:
        ui.navigate.to('/')
        return False
    return True

Base.metadata.create_all(bind=engine)

def seed_subjects():
    db = SessionLocal()
    if db.query(Subject).count() == 0:
        for s in DEFAULT_SUBJECTS:
            db.add(DEFAULT_SUBJECTS(
                name=s['name'],
                level=s['level'],
                grades=','.join(s['grades'])
            ))
        db.commit()
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
    ui.label('Teacher Dashboard – coming soon (Member C)')


if __name__ in {'__main__', '__mp_main__'}:
    Base.metadata.create_all(bind=engine)

    ui.run(
        title='EduSub',
        storage_secret='EduSub-secret-key-change-in-prod',
        port=8080,
        reload=False
    )

def handle_register():
    name  = name_input.value.strip()
    email = email_input.value.strip()
    pwd   = password_input.value
    role  = role_select.value

    # TEMP DEBUG — zeigt Fehler direkt auf der Seite
    try:
        if not name or not email or not pwd:
            error_label.set_text('All fields are required.')
            return
        if len(pwd) < 6:
            error_label.set_text('Password must be at least 6 characters.')
            return

        db: Session = SessionLocal()
        try:
            user = register_user(db, email, name, pwd, role)
        finally:
            db.close()

        if not user:
            error_label.set_text('This email is already registered.')
            return

        success_label.set_text(f'Welcome, {user.full_name}! Redirecting...')
        error_label.set_text('')
        ui.timer(1.5, lambda: ui.navigate.to('/'), once=True)

    except Exception as e:
        error_label.set_text(f'Error: {str(e)}')
