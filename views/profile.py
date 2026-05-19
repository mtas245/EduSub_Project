from nicegui import ui, app
from database import SessionLocal
from services.profile_service import ProfileService
from models.subject import Subject
from sqlmodel import select


def profile_view():
    db = SessionLocal()
    service = ProfileService(db)
    user_id = app.storage.user.get('user_id')
    user = service.get_profile(user_id)

    if not user:
        ui.navigate.to('/')
        return
    
    # Load all subjects and user subjects
    all_subjects = db.exec(select(Subject).order_by(Subject.name)).all()
    user_subjects = service.get_subjects(user_id)
    user_subjects_ids = [s.id for s in user_subjects]

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

            #Subjects multiselect
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
            
            service.update_profile(
                user_id=user_id,
                full_name=name,
                phone=phone,
                bio=bio_input.value,
            )
            selected_ids = subject_select.value or []
            service.set_subjects(user_id, selected_ids)
            ui.notify('Changes saved ✓', color='positive')

        ui.button('Save', icon='save', on_click=save).classes(
            'w-full mt-4 bg-blue-700 text-white rounded-lg py-2 hover:bg-blue800')
    
    db.close()

        
            
            
