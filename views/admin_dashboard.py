from nicegui import ui, app 
from database import SessionLocal
from services.request_service import RequestService
from datetime import date

def admin_dashboard():
    db = SessionLocal()
    svc = RequestService(db)

    full_name = app.storage.user.get('full_name', 'Admin')
    admin_id = app.storage.user.get('user_id')

    with ui.row().classes('w-full justify-between items-center p-4'
                          ' bg-blue-800 text-white'):
        ui.label(f'EduSub Admin - {full_name}').classes('text-xl font-bold')
        ui.button('Logout', on_click=lambda: ui.navigate.to('/logout'))
    with ui.column().classes('w-full p-6 gap-6'):
    
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

        with ui.card().classes('w-full p-4'):
            ui.label('Create New Substitute Request').classes('text-lg font-semibold mb-2')
            with ui.row().classes('gap-3 flex-wrap'):
                school_input = ui.input('School Name').classes('flex-1')
                subject_input = ui.input('Subject').classes('flex-1')
                grade_input = ui.select(
                    options=['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th'], 
                    label='Grade Level', value = '1st'
                ).classes('flex-1')
                date_input = ui.date(value=str(date.today())).classes('flex-1')
                note_input = ui.input('Additional Notes').classes('flex-1')

            result_label = ui.label('').classes('text-sm mt-1')

            def create_request():
                school = school_input.value.strip()
                subject = subject_input.value.strip()
                grade = grade_input.value
                dt = date_input.value

                if not school or not subject or not dt:
                    result_label.set_text('Please fill in all required fields.')
                    return

                from datetime import datetime
                date_obj = datetime.strptime(dt, '%Y-%m-%d').date()

                req = svc.create_request(
                    school_name=school,
                    subject=subject,
                    grade_level=grade,
                    date_obj=date_obj,
                    notes=note_input.value,
                    admin_id=admin_id       
                )
                result_label.set_text(f'Request created: {req.subject} on {req.date}')
                ui.navigate.to('/admin')

            ui.button('Create Request', on_click=create_request).classes('bg-blue-700 text-white mt-2')

        with ui.card().classes('w-full p-4'):
            ui.label('All Subbstitue Requests').classes('text-lg font-semibold mb-2')
            columns = [
                {'name': 'school', 'label': 'School', 'field': 'school'},
                {'name': 'subject', 'label': 'Subject', 'field': 'subject'},
                {'name': 'grade', 'label': 'Grade', 'field': 'grade'},
                {'name': 'date', 'label': 'Date', 'field': 'date'},
                {'name': 'status', 'label': 'Status', 'field': 'status'},
            ]
            rows = [
                {
                    'school': r.school_name,
                    'subject': r.subject,
                    'grade': r.grade_level,
                    'date': str(r.date),
                    'status': r.status.value
                }
                for r in all_requests
            ]
            ui.table(columns=columns, rows=rows).classes('w-full')

        with ui.card().classes('w-full p-4'):
            ui.label('Pending Applications - Approve or Reject').classes('text-lg font-semibold mb-2')
            if not pending_apps:
                ui.label('No pending applications at the moment.').classes('text-sm text-gray-400')
            else:
                for appl in pending_apps:
                    with ui.row().classes('items-center gap-4 border-b py-2'):
                        ui.label(f'Teacher Id {appl.teacher_id}').classes('flex-1')
                        ui.label(f'Request ID {appl.request_id}').classes('flex-1')
                        ui.label(f'Applied: {appl.applied_at}').classes('flex-1 text-sm')
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

                    


        


    
