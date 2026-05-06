from nicegui import ui, app
from database import SessionLocal
from models.user import User, Role
from services.profile_service import ProfileService
from sqlmodel import select


def admin_teacher_profile_view(teacher_id: int):
    db = SessionLocal()
    teacher = db.exec(select(User).where(User.id == teacher_id)).first()

    with ui.column().classes('w-full max-w-2xl mx-auto p-6'):
        with ui.row().classes('w-full items-center justify-between mb-6'):
            ui.label('Teacher Profile').classes('text-3xl font-bold')
            ui.button('← Back to Dashboard',
                      on_click=lambda: ui.navigate.to('/admin')).classes('bg-gray-100')

        if not teacher:
            ui.label('Teacher not found.').classes('text-red-500')
            db.close()
            return

        service = ProfileService(db)
        subjects = service.get_subjects(teacher_id)
        subject_names = ', '.join(s.name for s in subjects) if subjects else '-'

        # --- Staff Number + Approval Status ---
        with ui.card().classes('w-full p-4 mb-4 bg-blue-50'):
            with ui.row().classes('w-full justify-between items-center'):
                with ui.column():
                    ui.label('Staff Number').classes('text-xs text-gray-500')
                    ui.label(teacher.personal_number or '-').classes(
                        'text-2xl font-mono font-bold text-blue-700')
                if teacher.is_approved:
                    ui.badge('Approved', color='green').classes('text-white px-3 py-1')
                else:
                    ui.badge('Pending Approval', color='orange').classes('text-white px-3 py-1')

        # --- Profile Details ---
        with ui.card().classes('w-full p-6 mb-4'):
            ui.label('Profile Details').classes('text-xl font-bold mb-4')

            def field(label: str, value: str):
                with ui.row().classes('w-full gap-4 items-start py-2 border-b'):
                    ui.label(label).classes('text-gray-500 w-32 text-sm shrink-0')
                    ui.label(value or '-').classes('text-gray-900')

            field('Full Name', teacher.full_name)
            field('Email', teacher.email)
            field('Phone', teacher.phone)
            field('Subjects', subject_names)
            field('Bio', teacher.bio)
            
        # --- Documents ---
        with ui.card().classes('w-full p-6 mb-4'):
            ui.label('Documents').classes('text-xl font-bold mb-4')
            if teacher.documents_path:
                for path in teacher.documents_path.split(','):
                    path = path.strip()
                    filename = path.split('/')[-1].split('\\')[-1]
                    # Convert local path to URL
                    url = '/uploads/documents/' + filename
                    with ui.row().classes('items-center gap-2 py-1'):
                        ui.icon('attach_file').classes('text-blue-400')
                        ui.link(filename, url, new_tab=True).classes('text-sm text-blue-700 hover:underline')
            else:
                ui.label('No documents uploaded.').classes('text-sm text-gray-400')

        # --- Approve / Reject (only if pending) ---
        if not teacher.is_approved:
            with ui.card().classes('w-full p-6 border border-orange-200 bg-orange-50'):
                ui.label('Teacher Approval').classes('text-lg font-semibold mb-3')
                ui.label('Review the documents above before approving.').classes('text-sm text-gray-500 mb-4')
                with ui.row().classes('gap-3'):
                    ui.button('Approve Teacher', icon='check',
                              on_click=lambda: [
                                  service.approve_teacher(teacher_id),
                                  ui.navigate.to('/admin')
                              ]).classes('bg-green-600 text-white rounded-lg px-5 hover:bg-green-700')
                    ui.button('Reject & Delete', icon='close',
                              on_click=lambda: [
                                  service.reject_teacher(teacher_id),
                                  ui.navigate.to('/admin')
                              ]).classes('bg-red-500 text-white rounded-lg px-5 hover:bg-red-600')

    db.close()
