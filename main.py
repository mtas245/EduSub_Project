from nicegui import ui, app

from database import engine, Base
from views.admin_dashboard import admin_dashboard
from models.user import User
from models.request import SubstituteRequest, RequestStatus


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
        title='Edumatch',
        storage_secret='edumatch-secret-key-change-in-prod',
        port=8080,
        reload=False
    )