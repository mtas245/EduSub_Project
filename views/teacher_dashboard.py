from nicegui import ui, app
from database import SessionLocal
from services.request_service import RequestService
from services.application_service import ApplicationService
from models.subject import Subject
from sqlmodel import select
from datetime import datetime

SCHOOL_NAME = "Primarschule St. Johann"
SCHOOL_ADDRESS = "Elsässerstrasse 7, 4056 Basel"


def get_subject_name(db, subject_id: int) -> str:
    s = db.get(Subject, subject_id)
    return s.name if s else f'#{subject_id}'


def teacher_dashboard_view():
    db = SessionLocal()
    req_service = RequestService(db)
    app_service = ApplicationService(db)
    teacher_id = app.storage.user.get('user_id')
    full_name = app.storage.user.get('full_name', 'Teacher')

    # --- Header / Navbar ---
    with ui.row().classes('w-full items-center justify-between px-8 py-4 bg-blue-800 text-white shadow-md'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('school').classes('text-2xl text-blue-200')
            ui.label('EduSub').classes('text-xl font-bold tracking-wide text-white')
            ui.label(f'| {full_name}').classes('text-blue-300 text-sm')
        with ui.row().classes('gap-2'):
            ui.button('My Profile', icon='person',
                      on_click=lambda: ui.navigate.to('/profile')).classes(
                'bg-blue-700 text-white border border-blue-500 rounded-lg px-4 py-2 text-sm hover:bg-blue-600')
            ui.button('Logout', icon='logout',
                      on_click=lambda: (
                          app.storage.user.clear(),
                          ui.navigate.to('/')
                      )).classes('bg-transparent text-white border border-blue-500 rounded-lg px-4 py-2 text-sm hover:bg-blue-700')

    # --- Main Content ---
    with ui.column().classes('w-full max-w-4xl mx-auto p-6 gap-4'):

        with ui.tabs().classes('w-full') as tabs:
            tab_open = ui.tab('Available Assignments')
            tab_mine = ui.tab('My Assignments')

        with ui.tab_panels(tabs, value=tab_open).classes('w-full mt-2'):

            # ====== Tab 1: Available Assignments ======
            with ui.tab_panel(tab_open):

                with ui.row().classes('items-center gap-3 mb-4'):
                    ui.icon('filter_list').classes('text-gray-500')
                    grade_filter = ui.select(
                        label='Educational level',
                        options=['All', 'KG', 'Primary'],
                        value='All'
                    ).classes('w-56')

                now = datetime.now()
                valid = [r for r in req_service.get_open_requests()
                         if r.expires_at is None or r.expires_at > now]

                open_container = ui.column().classes('w-full gap-3')

                def render_open():
                    open_container.clear()
                    level = grade_filter.value
                    filtered = valid
                    if level == 'KG':
                        filtered = [r for r in valid if r.grade_level in ['KG1', 'KG2']]
                    elif level == 'Primary':
                        filtered = [r for r in valid if r.grade_level not in ['KG1', 'KG2']]

                    with open_container:
                        if not filtered:
                            with ui.column().classes('w-full items-center py-16 text-gray-400'):
                                ui.icon('event_busy').classes('text-5xl mb-2')
                                ui.label('No open assignments available.').classes('text-base')
                            return

                        for req in filtered:
                            already_applied = app_service.has_applied(teacher_id, req.id)

                            with ui.card().classes('w-full rounded-xl shadow-sm border border-gray-100'):
                                with ui.row().classes('w-full items-stretch'):
                                    ui.element('div').classes(
                                        'w-1 rounded-l-xl ' +
                                        ('bg-gray-300' if already_applied else 'bg-blue-500')
                                    )
                                    with ui.column().classes('flex-1 p-4 gap-1'):
                                        with ui.row().classes('w-full justify-between items-start'):
                                            with ui.column().classes('gap-1'):
                                                ui.label(f'{req.grade_level} – {get_subject_name(db, req.subject_id)}').classes(
                                                    'text-lg font-bold text-gray-800')
                                                with ui.row().classes('gap-4 text-sm text-gray-500 mt-1'):
                                                    with ui.row().classes('items-center gap-1'):
                                                        ui.icon('calendar_today').classes('text-base text-blue-400')
                                                        ui.label(req.date.strftime('%d.%m.%Y'))
                                                    if req.time_slot:
                                                        with ui.row().classes('items-center gap-1'):
                                                            ui.icon('schedule').classes('text-base text-blue-400')
                                                            ui.label(req.time_slot)
                                                    if req.expires_at:
                                                        hours = int(
                                                            (req.expires_at - datetime.now()).total_seconds() // 3600
                                                        )
                                                        col = 'text-red-500' if hours < 6 else 'text-gray-400'
                                                        with ui.row().classes(f'items-center gap-1 {col}'):
                                                            ui.icon('timer').classes('text-base')
                                                            ui.label(f'Expires in {hours}h')

                                                    with ui.row().classes('items-center gap-1'):
                                                        ui.icon('location_on').classes('text-base text-blue-400')
                                                        ui.label(f'{SCHOOL_NAME} - {SCHOOL_ADDRESS}').classes('text-sm text-gray-500')

                                            def make_apply(rid=req.id):
                                                def apply():
                                                    result = app_service.apply(
                                                        teacher_id=teacher_id,
                                                        request_id=rid
                                                    )
                                                    ui.notify(
                                                        result['message'],
                                                        color='positive' if result['success'] else 'negative'
                                                    )
                                                    render_open()
                                                return apply

                                            if already_applied:
                                                with ui.row().classes('items-center gap-1 text-gray-400 text-sm mt-1'):
                                                    ui.icon('check_circle').classes('text-green-400 text-base')
                                                    ui.label('Applied')
                                            else:
                                                ui.button('Apply', icon='send',
                                                          on_click=make_apply()).classes(
                                                    'bg-blue-600 text-white rounded-lg px-4 text-sm hover:bg-blue-700')

                grade_filter.on('update:model-value', lambda: render_open())
                render_open()

            # ====== Tab 2: My Assignments ======
            with ui.tab_panel(tab_mine):

                my_assignments = req_service.get_approved_assignments_for_teacher(teacher_id)

                if not my_assignments:
                    with ui.column().classes('w-full items-center py-16 text-gray-400'):
                        ui.icon('assignment_turned_in').classes('text-5xl mb-2')
                        ui.label('No confirmed assignments yet.').classes('text-base')
                else:
                    with ui.row().classes('items-center gap-2 mb-4'):
                        ui.icon('check_circle').classes('text-green-500 text-xl')
                        ui.label('Your confirmed substitute assignments').classes('text-sm text-gray-500')

                    for req in my_assignments:
                        with ui.card().classes('w-full rounded-xl shadow-sm border border-gray-100'):
                            with ui.row().classes('w-full items-stretch'):
                                ui.element('div').classes('w-1 rounded-l-xl bg-green-500')
                                with ui.column().classes('flex-1 p-4 gap-1'):
                                    with ui.row().classes('w-full justify-between items-start'):
                                        with ui.column().classes('gap-1'):
                                            ui.label(f'{req.grade_level} – {get_subject_name(db, req.subject_id)}').classes(
                                                'text-lg font-bold text-gray-800')
                                            with ui.row().classes('gap-4 text-sm text-gray-500 mt-1'):
                                                with ui.row().classes('items-center gap-1'):
                                                    ui.icon('calendar_today').classes('text-base text-green-400')
                                                    ui.label(req.date.strftime('%d.%m.%Y'))
                                                if req.time_slot:
                                                    with ui.row().classes('items-center gap-1'):
                                                        ui.icon('schedule').classes('text-base text-green-400')
                                                        ui.label(req.time_slot)
                                                with ui.row().classes('items-center gap-1'):
                                                    ui.icon('location_on').classes('text-base text-green-400')
                                                    ui.label(f'{SCHOOL_NAME} - {SCHOOL_ADDRESS}').classes('text-sm text-gray-500')
                                                if req.note:
                                                    with ui.row().classes('items-center gap-1 text-gray-400'):
                                                        ui.icon('notes').classes('text-base')
                                                        ui.label(req.note)
                                        ui.badge('Confirmed', color='green').classes('text-white text-xs px-2 py-1')

        db.close()

