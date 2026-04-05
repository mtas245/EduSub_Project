from nicegui import ui
from sqlalchemy.orm import Session
from database import SessionLocal
from auth import register_user


def register_page():

    with ui.card().classes('absolute-center').style(
        'width:420px; padding:2.5rem; border-radius:16px; box-shadow:0 4px 24px rgba(0,0,0,0.08);'
    ):
        ui.label('EduSub').classes('text-sm font-bold text-blue-600 mb-1')
        ui.label('Create your account').classes('text-2xl font-bold text-gray-800 mb-1')
        ui.label('Join the substitute teacher platform').classes('text-sm text-gray-400 mb-6')

        name_input     = ui.input('Full Name').classes('w-full mb-2')
        email_input    = ui.input('Email address').classes('w-full mb-2')
        password_input = ui.input('Password', password=True).classes('w-full mb-2')
        role_select    = ui.select(
            options=['teacher', 'admin'],
            label='Role',
            value='teacher'
        ).classes('w-full mb-4')

        error_label   = ui.label('').classes('text-red-500 text-sm mb-2')
        success_label = ui.label('').classes('text-green-600 text-sm mb-2')

        def handle_register():
            name  = name_input.value.strip()
            email = email_input.value.strip()
            pwd   = password_input.value
            role  = role_select.value

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

        ui.button('Create Account', on_click=handle_register).classes(
            'w-full mt-2'
        ).style(
            'background:#1d4ed8; color:white; border-radius:8px; padding:10px; font-weight:600;'
        )

        ui.separator().classes('my-4')

        with ui.row().classes('justify-center w-full'):
            ui.label('Already have an account?').classes('text-sm text-gray-400')
            ui.link('Sign in', '/').classes('text-sm text-blue-600 font-medium ml-1')