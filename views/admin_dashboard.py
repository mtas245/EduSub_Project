from nicegui import ui, app
from models.request import GRADE_LEVELS
from models.subject import Subject, DEFAULT_SUBJECTS
from models.user import User
from database import SessionLocal
from services.request_service import RequestService
from sqlmodel import select
from datetime import date, datetime, timedelta
import re

SUBJECTS_BY_GRADE = {
    'KG': ['Free Play', 'Movement', 'Crafts'],
    'Grade12': ['German', 'Mathematics', 'LNMG', 'Textiles & Crafts', 'Art (BG)', 'PE', 'Music'],
    'Grade34': ['German', 'Mathematics', 'LNMG', 'Textiles & Crafts', 'Art (BG)', 'PE', 'Music', 'French'],
    'Grade56': ['German', 'Mathematics', 'LNMG', 'Textiles & Crafts', 'Art (BG)', 'PE', 'Music', 'French', 'English'],
}


def get_subjects_for_grade(grade: str) -> list[str]:
    if grade in ('KG1', 'KG2'):
        return SUBJECTS_BY_GRADE['KG']
    num = int(''.join(filter(str.isdigit, grade))) if any(c.isdigit() for c in grade) else 0
    if num in (1, 2):
        return SUBJECTS_BY_GRADE['Grade12']
    elif num in (3, 4):
        return SUBJECTS_BY_GRADE['Grade34']
    return SUBJECTS_BY_GRADE['Grade56']


def get_subject_id(db, name: str) -> int | None:
    """Look up a Subject by name and return its id."""
    subject = db.exec(select(Subject).where(Subject.name == name)).first()
    if not subject:
        # Seed if missing
        for s in DEFAULT_SUBJECTS:
            if s['name'] == name:
                subject = Subject(name=s['name'], level=s['level'], grades=s['grades'])
                db.add(subject)
                db.commit()
                db.refresh(subject)
                break
    return subject.id if subject else None


def get_subject_name(db, subject_id: int) -> str:
    """Look up a Subject name by id."""
    subject = db.get(Subject, subject_id)
    return subject.name if subject else f'#{subject_id}'


def seed_subjects(db) -> None:
    """Insert DEFAULT_SUBJECTS into DB if table is empty."""
    existing = db.exec(select(Subject)).all()
    if not existing:
        for s in DEFAULT_SUBJECTS:
            db.add(Subject(name=s['name'], level=s['level'], grades=s['grades']))
        db.commit()


def admin_dashboard():
    db = SessionLocal()
    seed_subjects(db)
    svc = RequestService(db)
    full_name = app.storage.user.get('full_name', 'Admin')
    admin_id = app.storage.user.get('user_id')

    # --- Header ---
    with ui.row().classes('w-full items-center justify-between px-8 py-4 bg-blue-800 text-white shadow-md'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('school').classes('text-2xl text-blue-200')
            ui.label('EduSub').classes('text-xl font-bold tracking-wide text-white')
            ui.label('| Admin').classes('text-blue-300 text-sm')
            ui.label(f'– {full_name}').classes('text-blue-300 text-sm')
        ui.button('Logout', icon='logout',
                  on_click=lambda: ui.navigate.to('/logout')).classes(
            'bg-transparent text-white border border-blue-500 rounded-lg px-4 py-2 text-sm hover:bg-blue-700')

    with ui.column().classes('w-full max-w-5xl mx-auto p-6 gap-6'):

        all_requests = svc.get_all_requests()
        open_requests = svc.get_open_requests()
        pending_apps = svc.get_pending_applications()

        # --- Stats ---
        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('flex-1 p-5 rounded-xl shadow-sm border border-gray-100 text-center'):
                ui.icon('list_alt').classes('text-blue-400 text-2xl')
                ui.label(str(len(all_requests))).classes('text-4xl font-bold text-blue-700')
                ui.label('Total Requests').classes('text-gray-400 text-sm mt-1')
            with ui.card().classes('flex-1 p-5 rounded-xl shadow-sm border border-gray-100 text-center'):
                ui.icon('event_available').classes('text-green-400 text-2xl')
                ui.label(str(len(open_requests))).classes('text-4xl font-bold text-green-600')
                ui.label('Open Requests').classes('text-gray-400 text-sm mt-1')
            with ui.card().classes('flex-1 p-5 rounded-xl shadow-sm border border-gray-100 text-center'):
                ui.icon('pending_actions').classes('text-yellow-400 text-2xl')
                ui.label(str(len(pending_apps))).classes('text-4xl font-bold text-yellow-600')
                ui.label('Pending Applications').classes('text-gray-400 text-sm mt-1')

        # --- Create Request ---
        with ui.card().classes('w-full p-6 rounded-xl shadow-sm border border-gray-100'):
            with ui.row().classes('items-center gap-2 mb-4'):
                ui.icon('add_circle').classes('text-blue-500 text-xl')
                ui.label('Create New Substitute Request').classes('text-lg font-semibold')

            with ui.row().classes('gap-3 flex-wrap'):
                grade_select = ui.select(
                    options=GRADE_LEVELS,
                    label='Class / Grade',
                    value='1a'
                ).classes('flex-1')

                initial_subjects = get_subjects_for_grade('1a')
                subject_select = ui.select(
                    options=initial_subjects,
                    label='Subject',
                    value=initial_subjects[0]
                ).classes('flex-1')

                date_input = ui.date(value=str(date.today())).classes('flex-1')
                time_input = ui.input(label='Time Slot (e.g. 08:00-12:00)').classes('flex-1')
                note_input = ui.textarea(label='Additional Notes').classes('flex-1')

            def on_grade_change(e):
                # e.args is the new value string
                new_grade = e.args if isinstance(e.args, str) else grade_select.value
                new_subjects = get_subjects_for_grade(new_grade)
                subject_select.options = new_subjects
                subject_select.value = new_subjects[0]
                subject_select.update()

            grade_select.on('update:model-value', on_grade_change)

            def create_request():
                grade = grade_select.value
                subject_name = subject_select.value
                dt = date_input.value

                if not subject_name or not dt:
                    ui.notify('Please fill in all required fields.', color='negative')
                    return

                date_obj = datetime.strptime(dt, '%Y-%m-%d').date()

                if date_obj < date.today():
                    ui.notify('The date cannot be in the past.', color='negative')
                    return

                time_slot = time_input.value.strip() or None
                if time_slot:
                    if not re.match(r'^\d{2}:\d{2}-\d{2}:\d{2}$', time_slot):
                        ui.notify('Time slot must be in format HH:MM-HH:MM (e.g. 08:00-12:00).', color='negative')
                        return

                subject_id = get_subject_id(db, subject_name)
                if subject_id is None:
                    ui.notify('Subject not found in database.', color='negative')
                    return

                req = svc.create_request(
                    subject_id=subject_id,
                    grade_level=grade,
                    date_obj=date_obj,
                    time_slot=time_slot,
                    note=note_input.value,
                    admin_id=admin_id,
                )
                subject_display = get_subject_name(db, req.subject_id)
                ui.notify(
                    f'Request created: {subject_display} – {req.grade_level} on {req.date}',
                    color='positive'
                )
                ui.navigate.to('/admin')

            ui.button('Create Request', icon='send',
                      on_click=create_request).classes(
                'bg-blue-700 text-white rounded-lg px-5 py-2 mt-3 hover:bg-blue-800')

        # --- All Requests Table ---
        with ui.card().classes('w-full p-6 rounded-xl shadow-sm border border-gray-100'):
            with ui.row().classes('items-center gap-2 mb-4'):
                ui.icon('table_view').classes('text-blue-500 text-xl')
                ui.label('All Substitute Requests').classes('text-lg font-semibold')
            ui.label('Click on a row to see details.').classes('text-xs text-gray-400 mb-2')

            columns = [
                {'name': 'grade',     'label': 'Class',     'field': 'grade',     'align': 'left'},
                {'name': 'subject',   'label': 'Subject',   'field': 'subject',   'align': 'left'},
                {'name': 'date',      'label': 'Date',      'field': 'date',      'align': 'left'},
                {'name': 'time_slot', 'label': 'Time Slot', 'field': 'time_slot', 'align': 'left'},
                {'name': 'status',    'label': 'Status',    'field': 'status',    'align': 'left'},
            ]
            rows = [
                {
                    'id':         r.id,
                    'grade':      r.grade_level,
                    'subject':    get_subject_name(db, r.subject_id),
                    'date':       r.date.strftime('%d.%m.%Y') if r.date else '-',
                    'time_slot':  r.time_slot if r.time_slot else '-',
                    'status':     r.status.value,
                    'note':       r.note or '-',
                    'created_at': r.created_at.strftime('%d.%m.%Y %H:%M') if r.created_at else '-',
                    'expires_at': r.expires_at.strftime('%d.%m.%Y %H:%M') if r.expires_at else '-',
                }
                for r in all_requests
            ]

            with ui.dialog() as detail_dialog, ui.card().classes('p-6 min-w-96 rounded-xl'):
                ui.label('Request Details').classes('text-lg font-semibold mb-4')
                detail_grade   = ui.label('')
                detail_subject = ui.label('')
                detail_date    = ui.label('')
                detail_time    = ui.label('')
                detail_status  = ui.label('')
                detail_note    = ui.label('')
                detail_created = ui.label('')
                detail_expires = ui.label('')
                ui.button('Close', on_click=detail_dialog.close).classes(
                    'mt-4 bg-blue-700 text-white rounded-lg px-4')

            def on_row_click(e):
                row = e.args[1]
                detail_grade.set_text(f'Class:      {row["grade"]}')
                detail_subject.set_text(f'Subject:    {row["subject"]}')
                detail_date.set_text(f'Date:       {row["date"]}')
                detail_time.set_text(f'Time Slot:  {row["time_slot"]}')
                detail_status.set_text(f'Status:     {row["status"]}')
                detail_note.set_text(f'Note:       {row["note"]}')
                detail_created.set_text(f'Created:    {row["created_at"]}')
                detail_expires.set_text(f'Expires:    {row["expires_at"]}')
                detail_dialog.open()

            table = ui.table(columns=columns, rows=rows).classes('w-full cursor-pointer')
            table.on('rowClick', on_row_click)

        # --- Pending Applications ---
        with ui.card().classes('w-full p-6 rounded-xl shadow-sm border border-gray-100'):
            with ui.row().classes('items-center gap-2 mb-4'):
                ui.icon('pending_actions').classes('text-yellow-500 text-xl')
                ui.label('Pending Applications').classes('text-lg font-semibold')

            if not pending_apps:
                with ui.column().classes('w-full items-center py-8 text-gray-400'):
                    ui.icon('check_circle').classes('text-4xl mb-2 text-green-400')
                    ui.label('No pending applications at the moment.').classes('text-sm')
            else:
                for appl in pending_apps:
                    teacher = db.exec(select(User).where(User.id == appl.teacher_id)).first()
                    teacher_name = teacher.full_name if teacher else f'Teacher #{appl.teacher_id}'
                    teacher_pnr = teacher.personal_number if teacher else '-'

                    with ui.card().classes('w-full rounded-xl border border-gray-100 mb-3'):
                        with ui.row().classes('w-full items-stretch'):
                            ui.element('div').classes('w-1 rounded-l-xl bg-yellow-400')
                            with ui.row().classes('flex-1 p-4 justify-between items-center'):
                                with ui.column().classes('gap-1'):
                                    with ui.row().classes('items-center gap-2'):
                                        ui.icon('person').classes('text-base text-blue-400')
                                        ui.link(
                                            f'{teacher_pnr} ({teacher_name})',
                                            f'/admin/teacher/{appl.teacher_id}'
                                        ).classes('font-mono font-bold text-blue-700 hover:underline')
                                    with ui.row().classes('items-center gap-2 text-sm text-gray-400'):
                                        ui.icon('tag').classes('text-base')
                                        ui.label(f'Request ID: {appl.request_id}')
                                        ui.icon('schedule').classes('text-base ml-2')
                                        ui.label(
                                            appl.applied_at.strftime('%d.%m.%Y %H:%M') if appl.applied_at else '-'
                                        )
                                with ui.row().classes('gap-2'):
                                    app_id = appl.id
                                    ui.button('Approve', icon='check',
                                              on_click=lambda _, a=app_id: [
                                                  svc.approve_application(a),
                                                  ui.navigate.to('/admin')
                                              ]).classes('bg-green-600 text-white rounded-lg px-4 hover:bg-green-700')
                                    ui.button('Reject', icon='close',
                                              on_click=lambda _, a=app_id: [
                                                  svc.reject_application(a),
                                                  ui.navigate.to('/admin')
                                              ]).classes('bg-red-500 text-white rounded-lg px-4 hover:bg-red-600')

        db.close()