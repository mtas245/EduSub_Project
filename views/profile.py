from nicegui import ui, app, events
from database import SessionLocal
from services.profile_service import ProfileService
from models.subject import Subject
from sqlmodel import select
import os

PROFILE_PIC_DIR = 'uploads/profile_pictures'
os.makedirs(PROFILE_PIC_DIR, exist_ok=True)


def profile_view():
    db = SessionLocal()
    service = ProfileService(db)
    user_id = app.storage.user.get('user_id')
    user = service.get_profile(user_id)

    if not user:
        ui.navigate.to('/')
        return

    all_subjects = db.exec(select(Subject).order_by(Subject.name)).all()
    user_subjects = service.get_subjects(user_id)
    user_subjects_ids = [s.id for s in user_subjects]

    # Track new profile picture path
    new_profile_pic = {'path': None}

    with ui.column().classes('w-full max-w-2xl mx-auto p-6'):
        with ui.row().classes('w-full items-center justify-between mb-6'):
            ui.label('My Profile').classes('text-3xl font-bold')
            ui.button('Back', icon='arrow_back',
                      on_click=lambda: ui.navigate.to('/teacher')).classes(
                'bg-gray-100 text-gray-700 rounded-lg px-4')

        # Staff number
        with ui.card().classes('w-full p-4 mb-4 bg-blue-50'):
            ui.label('Your Staff Number').classes('text-xs text-gray-500')
            ui.label(user.personal_number or 'Not assigned yet').classes(
                'text-2xl font-mono font-bold text-blue-700')
            ui.label('Used by admins to identify you.').classes('text-xs text-gray-400')

        # Profile picture card
        with ui.card().classes('w-full p-6 mb-4'):
            ui.label('Profile Picture').classes('text-xl font-bold mb-4')
            with ui.row().classes('items-center gap-6'):
                # Current picture preview
                if user.profile_picture and os.path.exists(user.profile_picture):
                    pic_url = '/uploads/profile_pictures/' + os.path.basename(user.profile_picture)
                else:
                    pic_url = None

                avatar_container = ui.column().classes('items-center')
                with avatar_container:
                    if pic_url:
                        avatar = ui.image(pic_url).classes('rounded-full').style('width:100px; height:100px; object-fit:cover;')
                    else:
                        avatar = ui.icon('account_circle').classes('text-gray-300').style('font-size:100px;')

                with ui.column().classes('gap-2'):
                    ui.label('Upload a new profile picture').classes('text-sm text-gray-500')
                    ui.label('Accepted: JPG, PNG').classes('text-xs text-gray-400')

                    async def handle_pic_upload(e: events.UploadEventArguments):
                        filename = f'user_{user_id}_{e.file.name}'
                        dest = os.path.join(PROFILE_PIC_DIR, filename)
                        await e.file.save(dest)
                        new_profile_pic['path'] = dest
                        # Update preview
                        new_url = '/uploads/profile_pictures/' + filename
                        avatar_container.clear()
                        with avatar_container:
                            ui.image(new_url).classes('rounded-full').style('width:100px; height:100px; object-fit:cover;')
                        ui.notify('Picture uploaded — click Save to confirm.', color='info')

                    ui.upload(
                        label='Choose picture',
                        auto_upload=True,
                        on_upload=handle_pic_upload
                    ).props('accept=".jpg,.jpeg,.png"').classes('w-full')

        # Editable fields
        with ui.card().classes('w-full p-6'):
            ui.label('Edit Profile').classes('text-xl font-bold mb-4')

            name_input = ui.input('Full Name', value=user.full_name or '').classes('w-full')
            name_input.props('required')

            ui.input('Email (cannot be changed)', value=user.email or '').classes(
                'w-full').props('readonly')

            phone_input = ui.input('Phone', value=user.phone or '').classes('w-full')
            phone_input.props('required')

            bio_input = ui.textarea('Short Bio', value=user.bio or '').classes('w-full')

            ui.label('Subjects').classes('text-sm text-gray-500 mt-2')
            subject_select = ui.select(
                options={s.id: s.name for s in all_subjects},
                multiple=True,
                value=user_subjects_ids,
                label='Select your subjects'
            ).classes('w-full')

        def save():
            name = name_input.value.strip()
            phone = phone_input.value.strip()

            if not name:
                ui.notify('Full name is required.', color='negative')
                return
            if not phone:
                ui.notify('Phone number is required.', color='negative')
                return
            if not phone.isdigit():
                ui.notify('Phone must contain digits only.', color='negative')
                return

            update_kwargs = dict(full_name=name, phone=phone, bio=bio_input.value)
            if new_profile_pic['path']:
                update_kwargs['profile_picture'] = new_profile_pic['path']

            service.update_profile(user_id=user_id, **update_kwargs)
            selected_ids = subject_select.value or []
            service.set_subjects(user_id, selected_ids)
            ui.notify('Changes saved ✓', color='positive')

        ui.button('Save', icon='save', on_click=save).classes(
            'w-full mt-4 bg-blue-700 text-white rounded-lg py-2 hover:bg-blue-800')

    db.close()