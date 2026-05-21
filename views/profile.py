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
    new_profile_pic = {'path': None}

    # Navbar
    with ui.row().classes('w-full items-center justify-between px-8 py-4 bg-blue-900 text-white'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('school').classes('text-2xl text-blue-300')
            ui.label('EduSub').classes('text-xl font-bold text-white')
            ui.label('| My Profile').classes('text-blue-300 text-sm')
        ui.button('Back', icon='arrow_back',
                  on_click=lambda: ui.navigate.to('/teacher')).classes(
                      'bg-transparent text-white border border-blue-500 rounded-lg px-4 py-2 text-sm')
        
    with ui.column().classes('w-full max-w-2xl mx-auto px-6 py-6 gap-4'):

        # Staff number
        with ui.card().classes('w-full rounded-xl border border-blue-100 bg-blue-50 p-5'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('badge').classes('text-3xl text-blue-400')
                with ui.column().classes('gap-0'):
                    ui.label('Staff Number').classes('text-xs text-gray-400 font-medium')
                    ui.label(user.personal_number or 'Not assigned yet').classes(
                        'text-2xl font-mono font-bold text-blue-700')
                    ui.label('Used by admins to identify you.').classes('text-xs text-gray-400')

        # Profile picture
        with ui.card().classes('w-full rounded-xl border border-gray-100 p-5'):
            ui.label('Profile Picture').classes('text-base font-semibold text-gray-800 mb-4')
            with ui.row().classes('items-center gap-6'):
                avatar_container = ui.column().classes('items-center')
                with avatar_container:
                    if user.profile_picture and os.path.exists(user.profile_picture):
                        pic_url = '/uploads/profile_pictures/' + os.path.basename(
                            user.profile_picture)
                        ui.image(pic_url).classes('rounded-full border-4 border-blue-100').style(
                            'width:88px; height:88px; object-fit:cover;')
                    else:
                        with ui.element('div').classes(
                            'rounded-full bg-blue-50 border-2 border-blue-100 '
                            'flex items-center justify-center'
                        ).style('width:88px; height:88px;'):
                            ui.icon('account_circle').classes('text-blue-200').style(
                                'font-size:80px;')
                        
                with ui.column().classes('gap-2 flex-1'):
                    ui.label('Upload a new photo').classes('text-sm font-medium text-gray-700')
                    ui.label('JPG or PNG max 5 MB').classes('text-xs text-gray-400')

                    async def handle_pic_upload(e: events.UploadEventArguments):
                        filename = f'user_{user_id}_{e.file.name}'
                        dest = os.path.join(PROFILE_PIC_DIR, filename)
                        await e.file.save(dest)
                        new_profile_pic['path'] = dest
                        new_url = '/uploads/profile_pictures/' + filename
                        avatar_container.clear()
                        with avatar_container:
                            ui.image(new_url).classes(
                                'rounded-full border-4 border-blue-100').style(
                                    'width:88px; height:88px; object-fit:cover;')
                        ui.notify('Photo uploaded - click Save to confirm.', color='info')

                    ui.upload(
                        label='Choose photo',
                        auto_upload=True,
                        on_upload=handle_pic_upload
                    ).props('accept=".jpg,.jpeg,.png"').classes('w-full')

        # Edit profile
        with ui.card().classes('w-full rounded-xl border border-gray-100 p-5'):
            ui.label('Edit Profile').classes('text-base font-semibold text-gray-800 mb-4')
            
            name_input = ui.input('Full Name', value=user.full_name or '').classes(
                'w-full').props('outlined dense required')
            ui.input('Email (cannot be changed)', value=user.email or '').classes(
                'w-full').props('outlined dense readonly')
            phone_input = ui.input('Phone', value=user.phone or '').classes(
                'w-full').props('outlined dense required')
            bio_input = ui.textarea('Short Bio', value=user.bio or '').classes(
                'w-full').props('outlined rows=3')
            
            ui.separator().classes('my-3')
            ui.label('Subjects').classes('text-sm font-medium text-gray-600 mb-1')
            subject_select = ui.select(
                options={s.id: s.name for s in all_subjects},
                multiple=True,
                value=user_subjects_ids,
                label='Select subjects you can teach'
            ).classes('w-full').props('outlined dense use-chips')

        def save():
            name = name_input.value.strip()
            phone = phone_input.value.strip()

            if not name:
                ui.notify('Full name is required.', color='negative')
                return
            if not phone:
                ui.notify('Phone number must contain digits only.', color='negative')
                return
            
            update_kwargs = dict(full_name=name, phone=phone, bio=bio_input.value)
            if new_profile_pic['path']:
                update_kwargs['profile_picture'] = new_profile_pic['path']

            service.update_profile(user_id=user_id, **update_kwargs)
            selected_ids = subject_select.value or []
            service.set_subjects(user_id, selected_ids)
            ui.notify('Changes saved ✓', color='positive')

        ui.button('Save changes', icon='save', on_click=save).classes(
            'w-full bg-blue-700 text-white rounded-xl py-3 text-sm font-semibold '
            'hover:bg-blue-800')

    db.close()
            
            
            
            
                                
                            
                            
                        
                        
                    
                  