from nicegui import ui, app
from database import SessionLocal
from services.request_service import RequestService
from services.application_service import ApplicationService
from models.subject import Subject
from sqlmodel import select
from datetime import datetime

SCHOOL_NAME = "Primarschule St, Johann"
SCHOOL_ADDRESS = "Elsässerstrasse 7, 4056 Basel"

def get_subject_name(db, subject_id):
    """Retrieve subject name by ID from database."""
    subject = db.get(Subject, subject_id)
    return subject.name if subject else "Unknown"

def teacher_dashboard_view():
    db = SessionLocal()
    req_service = RequestService(db)
    app_service = ApplicationService(db)
    teacher_id = app.storage.user.get('user_id')
    full_name = app.storage.user.get('full_name', 'Teacher')

    # --- navbar ---
    with ui.row().classes('w-full items-center justify-between px-8 py-4 bg-blue-900 text-white shadow-md'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('school').classes('text-2xl text-blue-300')
            ui.label('EduSub').classes('text-xl font-bold tracking-wide text-white')
            ui.label(f'| {full_name}').classes('text-blue-300 text-sm')
        with ui.row().classes('gap-2'):
            ui.button('My Profile', icon='person', on_click=lambda: ui.navigate.to('/profile')).classes(
                'bg-blue-700 text-white border-blue-500 rounded-lg px-4 py-2 text-sm hover:bg-blue-600')
            ui.button('Logout', icon='logout',
                      on_click=lambda: (
                          app.storage.user.clear(),
                            ui.navigate.to('/')
                      )).classes('bg-transparent text-white border border-blue-500 rounded-lg px-4 py-2 text-sm hover:bg-blue-600')
            
    # --- main content ---
    with ui.column().classes('w-full max-w-4xl mx-auto px-6 py-6 gap-0'):

        with ui.tabs().classes('w-full') as tabs:
            tab_open = ui.tab('Available Assignments')
            tab_mine = ui.tab('My Assignments')

        with ui.tab_panel(tabs, value=tab_open).classes('w-full'):

            #-Tab 1: Available Assignments-#
            with ui.tab_panel(tab_open).classes('px-0'):

                now = datetime.now()
                valid = [r for r in req_service.get_open_requests()
                         if r.expires_at is None or r.expires_at > now] 

                # Filter bar #
                with ui.row().classes('items-center gap-3 py-4'):
                    ui.icon('tune').classes('text-gray-400 text-lg')
                    grade_filter = ui.select(
                        options=['All', 'KG', 'Primary'],
                        value='All',
                        label='level',
                    ).classes('w-44')
                    count_label = ui.label('').classes('ml-auto text-sm text-gray-400 bg-gray-100 px-3 py-1 rounded-full')

                    open_container = ui.column().classes('w-full gap-3')

                    def render_open():
                        open_container.clear()
                        level = grade_filter.value
                        filtered = valid
                        if level == 'KG':
                            filtered = [r for r in valid if r.grade_level in ['KG1', 'KG2']]
                        elif level == 'Primary':
                            filtered = [r for r in valid if r.grade_level not in ['KG1', 'KG2']]

                        count_label.set_text(f'{len(filtered)} assignment{"s" if len(filtered) != 1 else ""}')

                        with open_container:
                            if not filtered:
                                with ui.column().classes('w-full items-center py-20 gap-3'):
                                    with ui.element('div').classes('w-16 h-16 rounded-full bg-gray-100 felx items-center justify-center'):
                                        ui.icon('event_busy').classes('text-3xl text-gray-400')
                                    ui.label('No assignments available').classes('text-base font-medium text-gray-600')
                                    ui.label('There are no open substitute requests right now. Check back later or adjust the filter.').classes('text-sm text-gray-400 text-center max-w-xs')
                                    with ui.row().classes('items-center gap-1 text-xs text-gray-300 mt-1'):
                                        ui.icon('notifications').classes('text-sm')
                                        ui.label('New assigments will appear here automatically')
                                return
                            
                            for req in filtered:
                                already_applied = app_service.has_applied(teacher_id, req.id)
                                subject_name = get_subject_name(db, req.subject_id)
                                is_kg = req.grade_level in ['KG1', 'KG2']

                                accent = 'bg-gray-300' if already_applied else ('bg-green-500' if is_kg else 'bg-blue-600')
                                grade_bage = 'bg-green-50 text-green-700' if is_kg else 'bg-blue-50 text-blue-700'


                                    
                    

                      
            
                
            