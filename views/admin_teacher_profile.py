from nicegui import ui, app
from database import SessionLocal
from models.user import User, Role
from services.profile_service import ProfileService
from sqlmodel import select
import os

def admin_teacher_profile_view(teacher_id:int):
    db = SessionLocal()
    teacher = db.exec(select(User).where(User.id == teacher_id)).first()

    # Navbar
    with ui.row().classes('w-full items-center justify-between px-8 py-4 bg-blue-900 text-white'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('school').classes('text-2xl text-blue-300')
            ui.label('EduSub').classes('text-xl font-bold text-white')
            ui.label('| Teacher Profile').classes('text-blue-300 text-sm')
        ui.button('Back to Dashboard', icon='arrow_back',
                  on_click=lambda: ui.navigate.to('/admin')).classes(
                      'bg-transparent text-white border border-blue-500 rounded-lg px-4 py-2 text-sm')
        
    with ui.column().classes('w-full max-w-2xl mx-auto px-6 py-6 gap-4'):

        if not teacher:
            with ui.card().classes('w-full rounded-xl border border-red-100 bg-red-50 p-6'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('error').classes('text-red-400 text-xl')
                    ui.label('Teacher not found.').classes('text-red-600 font-medium')
            db.close()
            return
        
        service = ProfileService(db)
        subjects = service.get_subjects(teacher_id)
        subject_names = ', '.join(s.name for s in subjects) if subjects else '-'

        # Header card
        with ui.card().classes('w-full roundend-xl border border-gray-100 p-5'):
            with ui.row().classes('items-center gap-4'):
                # avatar
                if teacher.profile_picture and os.path.exists(teacher.profile_picture):
                    pic_url = '/uploads/profile_pictures/' + os.path.basename(
                        teacher.profile_picture)
                    ui.image(pic_url).classes('rounded-full border-4 border-blue-100').style(
                        'width:72px; height:72px; object-fit:cover;')
                else:
                    with ui.element('div').classes(
                        'rounded-full bg-blue-50 border-2 border-blue-100 '
                        'flex items-center justify-center flex-shrink-0'
                    ).style('width:72px; height:72px;'):
                        ui.label(teacher.full_name[:2].upper()).classes(
                            'text-xl font-bold text-blue-400')
                        
                with ui.column().classes('gap-1 flex-1'):
                    ui.label(teacher.full_name).classes('text-xl font-bold text-gray-800')
                    ui.label(teacher.email).classes('text-sm text-gray-400')

                if teacher.is_approved:
                    with ui.row().classes(
                            'items-center gap-1 bg-green-50 text-green-700 px-3 py-1 rounded-full'):
                        ui.icon('verified').classes('text-base')
                        ui.label('Approved').classes('text-xs font-semibold')
                else:
                    with ui.row().classes(
                            'items-center gap-1 bg-orange-50 text-orange-700 px-3 py-1 rounded-full'):
                        ui.icon('hourglass_empty').classes('text-base')
                        ui.label('Pending').classes('text-xs font-semibold')
                        
        # Staff number
        with ui.card().classes('w-full rounded-xl border border-blue-100 bg-blue p-4'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('badge').classes('text-2xl text-blue-400')
                with ui.column():
                    ui.label('Staff Number').classes('text-xs text-gray-400')
                    ui.label(teacher.personal_number or '-').classes(
                        'text-xl font-mono font-bold text-blue-700')
                    
        # Profile details
        with ui.card().classes('w-full rounded-xl border border-gray-100 p-5'):
            ui.label('Profile Details').classes('text-base font-semibold text-gray-800 mb-3')

            def field(icon_name: str, label: str, value: str):
                with ui.row().classes('w-full gap-3 items-start py-2 border-b border-gray-50'):
                    ui.icon(icon_name).classes('text-blue-300 text-base mt-0.5 flex-shrink-0')
                    ui.label(label).classes('text-gray-400 text-sm w-24 flex-shrink-0')
                    ui.label(value or '-').classes('text-gray-800 text-sm flex-1')

            field('phone', 'Phone', teacher.phone)
            field('school', 'Subjects', subject_names)
            field('notes', 'Bio', teacher.bio)

        # Documents
        with ui.card().classes('w-full rounded-xl border border-gray-100 p-5'):
            ui.label('Documents').classes('text-base font-semibold text-gray-800 mb-3')
            if teacher.documents_path:
                for path in teacher.documents_path.split(','):
                    path = path.strip()
                    filename = path.split('/')[-1].split('\\')[-1]
                    url = '/uploads/documents/' + filename
                    with ui.row().classes('items-center gap-2 py-2 border-b border-gray-50'):
                        ui.icon('attach_file').classes('text-blue-400 text-base')
                        ui.link(filename, url, new_tab=True).classes(
                            'text-sm text-blue-600 hover:underline flex-1')
                        ui.icon('open_in_new').classes('text-gray-300 text-sm')
            else:
                with ui.column().classes('items-center py-6 gap-2 text-gray-400'):
                    ui.icon('folder_open').classes('text-3xl')
                    ui.label('No documents uploaded').classes('text-sm')

        # Approve / Reject
        if not teacher.is_approved:
            with ui.card().classes('w-full rounded-xl border border-orange-200 bg-orange-50 p-5'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.icon('gavel').classes('text-orange-400 text-xl')
                    ui.label('Teacher Approval').classes(
                        'text-base font-semibold text-orange-800')
                ui.label('Review the profile and documents above before approving.').classes(
                    'text-sm text-orange-600 mb-4')
                with ui.row().classes('gap-3'):
                    ui.button('Approve Teacher', icon='check',
                              on_click=lambda: [
                                  service.approve_teacher(teacher_id),
                                  ui.navigate.to('/admin')
                              ]).classes(
                        'bg-green-600 text-white rounded-lg px-5 py-2 hover:bg-green-700')
                    ui.button('Reject & Delete', icon='close',
                              on_click=lambda: [
                                  service.reject_teacher(teacher_id),
                                  ui.navigate.to('/admin')
                              ]).classes(
                        'bg-red-500 text-white rounded-lg px-5 py-2 hover:bg-red-600')

    db.close()
                    