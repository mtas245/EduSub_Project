from nicegui import ui, app
from database import SessionLocal
from models.user import User

def admin_teacher_profile_view(teacher_id: int):
    db = SessionLocal()
    teacher = db.query(User).filter(User.id == teacher_id).first()
    db.close()

    with ui.column().classes('w-full max-w-2xl mx-auto p-6'):
        with ui.row().classes('w-full items-center justify-between mb-6'):
            ui.label('Teacher Profile').classes('text-3xl font-bold')
            ui.button('← Back to Dashboard',
                      on_click=lambda: ui.navigate.to('/admin')).classes('bg-gray-100')
            
        if not teacher:
            ui.label('Teacher not found.').classes('text-red-500')
            return
        
        with ui.card().classes('w-full p-4 mb-4 bg-blue-50'):
            ui.label('Staff Number').classes('text-xs text-gray-500')
            ui.label(teacher.personal_number or '-').classes(
                'text-2xl font-mono font-bold text-blue-700'
            )

        with ui.card().classes('w-full p-6'):
            ui.label('Profile Details').classes('text-xl font-bold mb-4')

            def field(label: str, value: str):
                with ui.row().classes('w-full gap-4 items-start py-2 border-b'):
                    ui.label(label).classes('text-gray-500 w-32 text-sm shrink-0')
                    ui.label(value or '-').classes('text-gray-900')

            field('Full Name', teacher.full_name)
            field('Email', teacher.email)
            field('Phone', teacher.phone)
            field('Subjects', teacher.subjects)
            field('Bio', teacher.bio)
    