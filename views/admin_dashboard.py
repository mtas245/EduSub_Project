from nicegui import ui, app 
from models.request import GRADE_LEVELS
from database import SessionLocal
from services.request_service import RequestService
from datetime import date, datetime, timedelta

#--- subject catalogue per grade group

SUBJECTS_BY_GRADE = {
    'KG': ['Free Play', 'Movement', 'Crafts'],
    'Grade12': ['German', 'Mathematics', 'LNMG', 'Textiles & Crafts', 'Art (BG)', 'PE', 'Music'],
    'Grade34': ['German', 'Mathematics', 'LNMG', 'Textiles & Crafts', 'Art (BG)', 'PE', 'Music', 'French'],
    'Grade56': ['German', 'Mathematics', 'LNMG', 'Textiles & Crafts', 'Art (BG)', 'PE', 'Music', 'French', 'English'], 
}

GRADE_LEVELS = GRADE_LEVELS

def get_subjects_for_grade(grade: str) -> list:
    if grade in ('KG1', 'KG2'):                 return SUBJECTS_BY_GRADE['KG']
    if grade in ('1a', '1b', '1c', '2a', '2b', '2c'): return SUBJECTS_BY_GRADE['Grade12']
    if grade in ('3a', '3b', '3c', '4a', '4b', '4c'): return SUBJECTS_BY_GRADE['Grade34']
    return SUBJECTS_BY_GRADE['Grade56']

def calculate_expires_at(assignment_date, time_slot: str = None):
    """"Returns the datetime 12 hours before the assignment starts."""
    from datetime import time as dt_time
    if time_slot:
        start_str   = time_slot.split('-')[0].strip()  # e.g. "08:00"
        hour, minute = map(int, start_str.split(':'))
        start_time = dt_time(hour, minute)
    else:
        start_time = dt_time(0, 0)
    assignment_dt = datetime.combine(assignment_date, start_time)
    return assignment_dt - timedelta(hours=12)


def admin_dashboard():
    db = SessionLocal()
    svc = RequestService(db)
    full_name = app.storage.user.get('full_name', 'Admin')
    admin_id = app.storage.user.get('user_id')

#--Header 
    with ui.row().classes('w-full justify-between items-center p-4'
                          ' bg-blue-800 text-white'):
        ui.label(f'EduSub Admin - {full_name}').classes('text-xl font-bold')
        ui.button('Logout', on_click=lambda: ui.navigate.to('/logout'))
    with ui.column().classes('w-full p-6 gap-6'):
    
    # -- Stats cards
        all_requests = svc.get_all_requests()
        open_requests = svc.get_open_requests()
        pending_apps = svc.get_pending_applications()

        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('p-4 min-w-32 text-center'):
                ui.label(str(len(all_requests))).classes('text-3xl font-bold text-blue-700')
                ui.label('Total Requests').classes('text-sm text-gray-500')
            with ui.card().classes('p-4 min-w-32 text-center'):
                ui.label(str(len(open_requests))).classes('text-3xl font-bold text-green-600')
                ui.label('Open').classes('text-sm text-gray-500')
            with ui.card().classes('p-4 min-w-32 text-center'):
                ui.label(str(len(pending_apps))).classes('text-3xl font-bold text-orange-500')
                ui.label('Pending Apps').classes('text-sm text-gray-500')

#-- Create new request form
        with ui.card().classes('w-full p-4'):
            ui.label('Create New Substitute Request').classes('text-lg font-semibold mb-2')
            with ui.row().classes('gap-3 flex-wrap'):

                #Grade dropdown - correct classes, no school_names
                grade_select = ui.select(
                    options=GRADE_LEVELS,
                    label='Class / Grade',
                    value='1a'
                ).classes('flex-1')

                # subject dropdown - update when grades changes 
                initial_subjects = get_subjects_for_grade('1a')
                subject_select = ui.select(
                    options=initial_subjects,
                    label='Subject',
                    value=initial_subjects[0]
                ).classes('flex-1')
            
                date_input = ui.date(value=str(date.today())).classes('flex-1')
                time_input = ui.input(label='Time Slot (e.g. 08:00-12:00)').classes('flex-1')
                note_input = ui.input(label='Additional Notes').classes('flex-1')

            result_label = ui.label('').classes('text-sm mt-1')

            # Update subject list when grade changes
            def on_grade_change(e):
                new_subjects = get_subjects_for_grade(e.value)
                subject_select.options = new_subjects
                subject_select.value = new_subjects[0]
                subject_select.update()
                
            grade_select.on('update:model-value', on_grade_change)

            def create_request():
                grade = grade_select.value
                subject = subject_select.value
                dt = date_input.value

                if not subject or not dt:
                    result_label.set_text('Please fill in all required fields.')
                    return
                
                date_obj = datetime.strptime(dt, '%Y-%m-%d').date()
                expires_at = calculate_expires_at(date_obj, time_input.value or None)

                req = svc.create_request(
                    subject=subject,
                    grade_level=grade,
                    date_obj=date_obj,
                    note=note_input.value,
                    admin_id=admin_id,
                )

                result_label.set_text(
                    f'Request created: {req.subject} - {req.grade_level} on {req.date}'
                )
                ui.navigate.to('/admin') 

            ui.button('Create Request', on_click=create_request).classes(
                'bg-blue-700 text-white mt-2')
            
            #All requests table

        with ui.card().classes('w-full p-4'):
            ui.label('All Substitute Requests').classes('text-lg font-semibold mb-2')

            columns = [
                {'name': 'grade', 'label': 'Class', 'field': 'grade'},
                {'name': 'subject', 'label': 'Subject', 'field': 'subject'},
                {'name': 'date', 'label': 'Date', 'field': 'date'},
                {'name': 'status', 'label': 'Status', 'field': 'status'},
            ]
            rows = [
                {
                    'grade': r.grade_level,
                    'subject': r.subject,
                    'date': r.date.strftime('%Y-%m-%d') if r.date else '-',
                    'status': r.status.value
                }
                for r in all_requests
            ]
            ui.table(columns=columns, rows=rows).classes('w-full')

            # Pending applications 
        with ui.card().classes('w-full p-4'):
            ui.label('Pending Applications - Approve or Reject').classes(
                'text-lg font-semibold mb-2')

            if not pending_apps:
                ui.label('No pending applications at the moment.').classes(
                    'text-sm text-gray-400')
            else:
                for appl in pending_apps:
                    with ui.row().classes('items-center gap-4 border-b py-2'):
                        ui.label(f'Teacher ID: {appl.teacher_id}').classes('flex-1')
                        ui.label(f'Request ID: {appl.request_id}').classes('flex-1')
                        ui.label(f'Applied at: {appl.applied_at.strftime("%Y-%m-%d %H:%M:%S") if appl.applied_at else "-"}').classes(
                            'flex-1 text-sm text-gray-500')
                        app_id = appl.id
                        ui.button(
                            'Approve',
                            on_click=lambda _, a=app_id: [
                                svc.approve_application(a),
                                ui.navigate.to('/admin')
                            ]
                        ).classes('bg-green-600 text-white')
                        ui.button(
                            'Reject',
                            on_click=lambda _, a=app_id: [
                                svc.reject_application(a),
                                ui.navigate.to('/admin')
                            ]
                        ).classes('bg-red-600 text-white')
    db.close()
    
    