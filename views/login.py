from nicegui import ui, app
from database import SessionLocal
from auth import login_user, verify_password
from models.user import Role, User
from sqlmodel import select


def login_page():
    """Render the login page."""

    if app.storage.user.get('logged_in'):
        role = app.storage.user.get('role')
        if role == 'admin':
            ui.navigate.to('/admin')
        else:
            ui.navigate.to('/teacher')
        return

    with ui.column().classes('absolute-center items-center').style('width:420px;'):

        with ui.column().classes('items-center mb-8 gap-1'):
            ui.icon('school').classes('text-5xl text-blue-700')
            ui.label('EduSub').classes('text-3xl font-bold text-blue-800')
            ui.label('Substitute Teacher Platform').classes('text-sm text-gray-400')

        with ui.card().classes('w-full rounded-2xl shadow-lg').style('padding:2rem;'):
            ui.label('Sign in to your account').classes('text-xl font-semibold text-gray-800 mb-1')
            ui.label('Enter your credentials below').classes('text-sm text-gray-400 mb-6')

            email_input = ui.input(
                'Email address',
                placeholder='you@example.com'
            ).classes('w-full mb-2').props('outlined dense')

            password_input = ui.input(
                'Password',
                password=True,
                password_toggle_button=True,
            ).classes('w-full mb-4').props('outlined dense')

            error_label = ui.label('').classes('text-red-500 text-sm mb-2 min-h-5')

            def handle_login():
                email = email_input.value.strip()
                password = password_input.value

                if not email or not password:
                    error_label.set_text('Please fill in all fields.')
                    return

                db = SessionLocal()
                try:
                    raw_user = db.exec(select(User).where(User.email == email)).first()
                    if (raw_user
                            and raw_user.role == Role.TEACHER
                            and not raw_user.is_approved
                            and verify_password(password, raw_user.password_hash)):
                        error_label.set_text('Your account is pending approval by an admin.')
                        return

                    user = login_user(db, email, password)
                finally:
                    db.close()

                if not user:
                    error_label.set_text('Invalid email or password.')
                    return

                app.storage.user['logged_in'] = True
                app.storage.user['user_id'] = user.id
                app.storage.user['full_name'] = user.full_name
                app.storage.user['role'] = user.role.value

                if user.role == Role.ADMIN:
                    ui.navigate.to('/admin')
                else:
                    ui.navigate.to('/teacher')

            ui.button('Sign In', icon='login', on_click=handle_login).classes(
                'w-full bg-blue-700 text-white rounded-lg py-3 text-sm font-semibold '
                'hover:bg-blue-800 mt-2')

            ui.separator().classes('my-5')

            with ui.row().classes('justify-center items-center gap-1 w-full'):
                ui.label('No account yet?').classes('text-sm text-gray-400')
                ui.link('Register here', '/register').classes(
                    'text-sm text-blue-600 font-medium hover:underline')