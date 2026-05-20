from nicegui import ui, app
from database import SessionLocal
from services.request_service import RequestService
from services.application_service import ApplicationService
from models.subject import Subject
from sqlmodel import select
from datetime import datetime

SCHOOL_NAME = "Primarschule St, Johann"
SCHOOL_ADDRESS = "Elsässerstrasse 7, 4056 Basel"

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

                                with ui.card().classes('w-full rounded-xl border border-gray-100 shadow-none'):
                                    with ui.row().classes('w-full items-stretch'):
                                        ui.element('div').classes(f'w-1 rounded-l-xl {accent}')
                                        with ui.column().classes('flex-1 p-4 gap-2'):
                                            # top row title + grade badge
                                            with ui.row().classes('w-full justify-between items-center'):
                                                ui.label(subject_name).classes('text-base font-semibold text-gray-800')
                                                ui.label(req.grade_level).classes(f'text-xs font-semibold px-3 py-1 rounded-full {grade_bage}')

                                            # meta row
                                            with ui.row().classes('gap-4 text-sm text-gray-500 flex-wrap'):
                                                with ui.row().classes('items-center gap-1'):
                                                    ui.icon('calender_today').classes('text-sm text-blue-400')
                                                    ui.label(req.date.strftime('%d.%m.%Y'))
                                                if req.time_slot:
                                                    with ui.row().classes('items-center gap-1'):
                                                        ui.icon('schedule').classes('text-sm text-blue-400')
                                                        ui.label(req.time_slot)
                                                if req.expires_at:
                                                    hours = int((req.expires_at - datetime.now()).total_seconds() // 3600)
                                                    exp_col = 'text-red-500' if hours < 6 else 'text-gray-400'
                                                    with ui.row().classes(f'items-center gap-1 {exp_col}'):
                                                        ui.icon('hourglass_empty').classes('text-sm')
                                                        ui.label(f'Expires in {hours}h')

                                            # Footer row location + action
                                            with ui.row().classes('w-full justify-between items-center mt-1'):
                                                with ui.row().classes('items-center gap-1 text-xs text-gray-400'):
                                                    ui.icon('location_on').classes('text-sm')
                                                    ui.label(f'{SCHOOL_NAME} · {SCHOOL_ADDRESS}')

                                                def make_apply(rid=req.id):
                                                    def apply():
                                                        result = app_service.apply(
                                                            teacher_id=teacher_id,
                                                            request_id=rid,
                                                        )
                                                        ui.notify(
                                                            result['message'],
                                                            color='positive' if result['success'] else 'negative'
                                                        )
                                                        render_open()
                                                    return apply
                                                
                                                if already_applied:
                                                    with ui.row().classes('items-center gap-1 text-sm text-green-600 font-medium'):
                                                        ui.icon('check_circle').classes('text-base')
                                                        ui.label('Applied')
                                                else:
                                                    ui.button('Apply', icon='send',
                                                              on_click=make_apply()).classes('bg-blue-600 text-white rounded-lg px-4 py-2 text-sm hover:bg-blue-700')
                                                    
                                            grade_filter.on('update:model-value', lambda: render_open())
                                            render_open()

                                            # Tab 2: My Assignments
                                            with ui.tab_panel(tab_mine).classes('px-0'):

                                                my_assignments = req_service.get_approved_assignments_for_teacher(teacher_id)

                                                if not my_assignments:
                                                    with ui.column().classes('w-full items-center py-20 gap-3'):
                                                        with ui.element('div').classes('w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center'):
                                                            ui.icon('assignment_turned_in').classes('text-3xl text-gray-400')
                                                        ui.label('No confirmed assignments yet').classes('text-base font-medium text-gray-600')
                                                        ui.label('Once an admin approves your application, your assignments will appear here.').classes('text-sm text-gray-400 text-center max-w-xs')
                                                else:
                                                    with ui.row().classes('items-center gap-2 py-4'):
                                                        ui.icon('check_circle').classes('text-green-500 text-lg')
                                                        ui.label(f'{len(my_assignments)} confirmed assignment{"s" if len(my_assignments) != 1 else ""}').classes('text-sm font-medium text-gray-600')

                                                    with ui.column().classes('w-full gap-3'):
                                                        for req in my_assignments:
                                                            subject_name = get_subject_name(db, req.subject_id)
                                                            is_kg = req.grade_level in ['KG1', 'KG2']
                                                            grade_bage = 'bg-green-50 text-green-700' if is_kg else 'bg-blue-50 text-blue-700'

                                                            with ui.card().classes('w-full rounded-xl border border-gray-100 shadow-none'):
                                                                with ui.row().classes('w-full items-stretch'):
                                                                    ui.element('div').classes('w-1 rounded-l-xl bg-green-500')
                                                                    with ui.column().classes('flex-1 p-4 gap-2'):
                                                                        with ui.row().classes('w-full justify-between items-center'):
                                                                            ui.label(subject_name).classes('text-base font-semibold text-gray-800')
                                                                            with ui.row().classes('items-center gap-2'):
                                                                                ui.label(req.grade_level).classes(f'text-xs font-semibold px-3 py-1 rounded-full {grade_bage}')
                                                                                ui.badge('Confirmed', color='green').classes('text-white text-xs')
                                                                        with ui.row().classes('gap-4 text-sm text-gray-500 flex-wrap'):
                                                                            with ui.row().classes('items-center gap-1'):
                                                                                ui.icon('calender_today').classes('text-sm text-green-400')
                                                                                ui.label(req.date.strftime('%d.%m.%Y'))
                                                                            if req.time_slot:
                                                                                with ui.row().classes('items-center gap-1'):
                                                                                    ui.icon('schedule').classes('text-sm text-green-400')
                                                                                    ui.label(req.time_slot)
                                                                            with ui.row().classes('items-center gap-1'):
                                                                                ui.icon('location_on').classes('text-sm text-green-400')
                                                                                ui.label(f'{SCHOOL_NAME} · {SCHOOL_ADDRESS}').classes('text-xs text-gray-400')

                                                                        if req.note:
                                                                            with ui.row().classes('items-center gap-1 text-xs text-gray-400'):
                                                                                ui.icon('notes').classes('text-sm')
                                                                                ui.label(req.note)


                      
            
                
            