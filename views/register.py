import os
import shutil
from nicegui import ui, events
from database import SessionLocal
from auth import register_user


UPLOAD_DIR = 'uploads/documents'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def register_page():
    uploaded_files: list[str] = []

    with ui.column().classes('w-full items-center py-8 px-4'):
        with ui.card().classes('w-full rounded-2xl shadow-lg').style(
            'max-width:480px; padding:2rem;'
        ):
            # Header
            with ui.row().classes('items-center gap-2 mb-1'):
                ui.icon('school').classes('text-2xl text-blue-700')
                ui.label('EduSub').classes('text-lg font-bold text-blue-700')

            ui.label('Create your account').classes('text-2xl font-bold text-gray-800 mb-1')
            ui.label('Join the substiute teacher platform').classes(
                'text-sm text-gray-400 mb-5')
            
            name_input = ui.input('Full Name', placeholder='Jane Teacher').classes('w-full mb-1').props('outlined dense required')
            email_input = ui.input('Email address', placeholder='you@example.com').classes('w-full mb-1').props('outlined dense required')
            phone_input = ui.input('Phone (digits only)', placeholder='0791234567').classes('w-full mb-1').props('outlined dense required')
            password_input = ui.input('Password', password=True,
                                      password_toggle_button=True).classes('w-full mb-1').props('outlined dense required')
            role_select = ui.select(
                options=['teacher', 'admin'],
                label='Role',
                value='teacher'
            ).classes('w-full mb-3').props('outlined dense')

            # Document upload (teacher only)
            upload_section = ui.column().classes('w-full mb-3')
            with upload_section:
                with ui.row().classes('items-center gap-2 mb-1'):
                    ui.icon('upload_file').classes('text-blue-400 text-lg')
                    ui.label('Upload Documents').classes('text-sm font-semibold text-gray-700')
                ui.label('Certificates, qualifications · PDF, JPG, PNG').classes(
                    'text-xs text-gray-400 mb-2')
                upload_status = ui.label('No files uploaded yet.').classes(
                    'text-xs text-gray-400 mb-1')
                
                async def handle_upload(e: events.UploadEventArguments):
                    filename = e.file.name
                    dest_path = os.path.join(UPLOAD_DIR, filename)
                    await e.file.save(dest_path)
                    uploaded_files.append(dest_path)
                    upload_status.set_text(
                        f'{len(uploaded_files)} file(s) uploaded: {", ".join(os.path.basename(p) for p in uploaded_files)}'
                    )
                    upload_status.classes(remove='text-gray-400', add='text-green-600')

                ui.upload(
                    label='Choose files',
                    multiple=True,
                    auto_upload=True,
                    on_upload=handle_upload
                ).props('accept=".pdf,.jpg,.jpeg,.png"').classes('w-full')

            def on_role_change(e):
                upload_section.set_visibility(role_select.value == 'teacher')

            role_select.on('update:model-value', on_role_change)

            error_label = ui.label('').classes('text-red-500 text-sm mb-1 min-h-4')

            def handle_register():
                name = name_input.value.strip()
                email = email_input.value.strip()
                phone = phone_input.value.strip()
                pwd = password_input.value
                role = role_select.value

                if not name or not email or not phone or not pwd:
                    error_label.set_text('Please fill in all required fields.')
                    return
                if not phone.isdigit():
                    error_label.set_text('Phone number must contain digits only.')
                    return
                if len(pwd) < 6:
                    error_label.set_text('Password must be at least 6 characters long.')
                    return
                
                documents_path = ','.join(uploaded_files) if uploaded_files else None

                db = SessionLocal()
                try:
                    user = register_user(db, email, name, pwd, role,
                                         phone=phone, documents_path=documents_path)
                finally:
                    db.close()

                if not user:
                    error_label.set_text('This email is already registered.')
                    return
                
                ui.notify(f'Welcome, {user.full_name}! Redirecting...', color='positive')
                ui.timer(1.5, lambda: ui.navigate.to('/'), once=True)

            ui.button('Create Account', icon='person_add',
                      on_click=handle_register).classes(
                          'w-full bg-blue-700 text-white rounded-lg py-3 text-sm font-semibold hover:bg-blue-800 mt-2')
            
            ui.separator().classes('my-4')

            with ui.row().classes('justify-center items-center gap-1 w-full'):
                ui.label('Already have an account?').classes('text-sm text-gray-400')
                ui.link('Sign in', '/').classes('text-sm text-blue-600 font-medium hover:underline')
                      
                
                
            