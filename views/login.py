from nicegui import ui, app
from sqlalchemy.orm import Session
from database import SessionLocal
from auth import login_user
from models import user
from models.user import Role

def login_page():
    '''Render the login page.'''

    # If already logged in, redirect immediately
    if app.storage.user.get('logged_in'):
        role = app.storage.user.get('role')
        if role == 'admin':
            ui.navigate.to('/admin')
        else:
            ui.navigate.to('/teacher')
        return

    with ui.card().classes('absolute-center').style('width:380px; padding:2rem;'):
        ui.label('EduSub').classes('text-2xl font-bold text-blue-700')
        ui.label('Sign in to your account').classes('text-gray-500 mb-4')

        email_input = ui.input('Email address').classes('w-full')
        password_input = ui.input('Password', password=True).classes('w-full')
        error_label = ui.label('').classes('text-red-500 text-sm')

        def handle_login():
            email = email_input.value.strip()
            password = password_input.value

            if not email or not password:
                error_label.set_text('Please fill in all fields.')
                return
            db: Session = SessionLocal()
            try:
                user = login_user(db, email, password)
            finally:
                db.close()

            if not user:
                error_label.set_text('Invalid email or password')
                return

            app.storage.user['logged_in'] = True
            app.storage.user['user_id'] = user.id
            app.storage.user['full_name'] = user.full_name
            app.storage.user['role'] = user.role.value

            if user.role == Role.ADMIN:
                ui.navigate.to('/admin')
            else:
                ui.navigate.to('/teacher')

        ui.button('Sign In', on_click=handle_login).classes(
            'w-full bg-blue-700 text-white mt-2'
        )
        ui.separator()
        ui.label('No account yet?').classes('text-sm text-gray-400')
        ui.link('Register here', '/register').classes('text-sm text-blue-600')
