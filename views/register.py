import os
import shutil
from nicegui import ui, events
from database import SessionLocal
from auth import register_user


UPLOAD_DIR = 'uploads/documents'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def register_page():
    uploaded_files: list[str] = []

    with ui.card().classes('absolute-center').style(
        'width:460px; padding:2.5rem; border-radius:16px; box-shadow:0 4px 24px rgba(0,0,0,0.08);'
    ):
        ui.label('EduSub').classes('text-sm font-bold text-blue-600 mb-1')
        ui.label('Create your account').classes('text-2xl font-bold text-gray-800 mb-1')
        ui.label('Join the substitute teacher platform').classes('text-sm text-gray-400 mb-6')

        name_input = ui.input('Full Name').classes('w-full mb-2').props('required')
        email_input = ui.input('Email address').classes('w-full mb-2').props('required')
        phone_input = ui.input('Phone (digits only)').classes('w-full mb-2').props('required')
        password_input = ui.input('Password', password=True).classes('w-full mb-2').props('required')
        role_select = ui.select(
            options=['teacher', 'admin'],
            label='Role',
            value='teacher'
        ).classes('w-full mb-4')

        # --- Document upload /only for teachers ---
        upload_section = ui.column().classes('w-full mb-4')
        with upload_section:
            ui.label('Upload Documents (certificates, qualifications)').classes('text-sm text-gray-500 mb-1')
            ui.label('Accepted: PDF, JPG, PNG').classes('text-xs text-gray-400 mb-2')
            upload_status = ui.label('No files uploaded yet.').classes('text-xs text-gray-400')

            def handle_uploade(e: events.UploadEventArguments):
                filename = e.name
                dest_path = os.path.join(UPLOAD_DIR, filename)
                with open(dest_path, 'wb') as f:
                    f.write(e.content.read())
                uploaded_files.append(dest_path)
                upload_status.set_text(f'{len(uploaded_files)} file(s) uploaded: {", ".join(os.path.basename(p) for p in uploaded_files)}')

            ui.upload(
                label='Choose files',
                multiple=True,
                auto_upload=True,
                on_upload=handle_uploade
            ).props('accept=".pdf,.jpg,.jpeg,.png"').classes('w-full')

        def on_role_change(e):
            upload_section.set_visibility(role_select.value == 'teacher')

        role_select.on('update:model-value', on_role_change)

        error_label = ui.label('').classes('text-red-500 text-sm mb-2')
        success_label = ui.label('').classes('text-green-600 text-sm mb-2')

        def handle_register():
            name = name_input.value.strip()
            email = email_input.value.strip()
            phone = phone_input.value.strip()
            pwd = password_input.value
            role = role_select.value

            if not name or not email or not phone or not pwd:
                error_label.set_text('All fields are required.')
                return
            if not phone.isdigit():
                error_label.set_text('Phone must contain digits only.')
                return
            if len(pwd) < 6:
                error_label.set_text('Password must be at least 6 characters.')
                return
            
            # Save documents_path as seperat list
            documents_path = ','.join(uploaded_files) if uploaded_files else None

            db = SessionLocal()
            try:
                user = register_user(db, email, name, pwd, role, phone=phone, documents_path=documents_path)
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

            