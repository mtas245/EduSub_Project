from nicegui import ui
from sqlalchemy.orm import Session
from database import SessionLocal
from auth import register_user


def register_page():
    '''Render the registration page.'''

    with ui.card().classes('absolute-center').style('width:400px; padding:2rem;'):
        ui.label('Create Account').classes('text-2xl font bold text-blue-700')
        ui.label('Join Edumatch').classes('text-gray-500 mb-4')

    name_input = ui.input('Full Name').classes('w-full')
    email_input = ui.input('Email address').classes('w-full')
    password_input = ui.input('Password', password=True).classes('w-full')
    role_select = ui.select(
        options=['teacher', 'admin'],
        label= 'Role',
        value= 'teacher'
    ).classes('w-full')
    error_label = ui.label('').classes('text-red-500 text-sm')
    success_label = ui.label('').classes('text-green-600 text-sm')

    def handle_register():
        name = name_input.value.strip()
        email = email_input.value.strip()
        pwd = password_input.value
        role = role_select.value

        if not name or not email or not pwd:
            error_label.set_text('All fields are required')
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

        success_label.set_text(f'Account created! Welcome, {user.full_name}.')
        error_label.set_text('')

        #Redirect to login after short delay
        ui.timer(1.5, lambda: ui.navigate.to('/'), once=True)

    ui.button('Register', on_click=handle_register).classes(
        'w-full bg-blue-700 text-white mt-2'
    )
    ui.link('Already have an account? Sign in', '/').classes('text-sm text-blue-600 mt-2')