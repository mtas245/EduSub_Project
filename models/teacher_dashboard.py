# Add in main.py
from models.application import Application  # noqa:  F401
from views.teacher_dashboard import teacher_dashboard
from nicegui import (ui, app)
from sqlalchemy.dialects.mssql.information_schema import columns

from database import SessionLocal
from models.application import request_id
from services.application_service import ApplicationService


def teacher_dashboard():
    """Teacher Dashboard - browse requests and manage applications."""
    db = SessionLocal()
    svc = ApplicationService(db)

    full_name = app.storage.user.get('full_name', "Teacher")
    teacher_id = app.storage.user.get('user_id')

    # ── Top bar ──────────────────────────────────────────
    with ui.row().classes('w-full justify-between items -center p-4 bg-green-800 text-white'):
        ui.label(f'SubConnect - {full_name}').classes('text-xl font-bold')
        ui.button('Logout', on_click=lambda: ui.navigate.to('/logout'))

    with ui.column().classes('w-full p-6 gap-6'):

    # ── Open Requests panel ───────────────────────────
    with ui.card().classes('w-full p-4'):
        ui.label('Available Substitute Requests').classes('text-xl font-bold mb-2')
        open_request = svc.get_open_requests()

        if not open_request:
            ui.label('No open requests at the moment.').classes('text-gray-400')
        else:
            # Header row
            with ui.row().classes('font-bold text-gray-600 border-b pb-1'):
                ui.label('School').classes('w-40')
                ui.label('Subject').classes('w-32')
                ui.label('Grade').classes('w-20')
                ui.label('Date').classes('w-28')
                ui.label('Notes').classes('flex-1')
                ui.label('Action').classes('w-28')

            for req in open_request:
                already_applied = svc.has_applied(teacher_id, req.id)
                with ui.row().classes('items-center border-b py-2'):
                    ui.label(req.school_name).classes('w-40')
                    ui.label(req.subject).classes('w-32')
                    ui.label(req.grade).classes('w-20')
                    ui.label(req.date).classes('w-28')
                    ui.label(req.notes or '-').classes('flex-1 text-sm text gray-500')
                    req_id = req.id
                    if already_applied:
                        ui.label('Applied').classes('w-28 text-green-600 text-sm')
                    else:
                        def apply_click(_, rid=req_id):
                            result = svc.apply(teacher_id, rid)
                            if result['success']:
                                ui.notify(result['message'], type='positive')
                            else:
                                ui.notify(result['message'], type='warning')
                                ui.navigate.to('/teacher')

                                ui.button('Apply', on_click=apply_click).classes('w-28 bg-green-600 text-white text-sm')

                                # ── My Applications panel ─────────────────────────
                                with ui.card().classes('w-full p-4'):
                                    ui.label('My Applications').classes('text-lg font-bold mn-2')

                                    my_apps = svc.get_my_applications(teacher_id)

                                    if not my_apps:
                                        ui.label('You have not applied for any requests yet').classes('text-gray-400')
                                    else:
                                        columns = [
                                            {'name': 'request', 'label': 'Request ID', 'field': 'request'},
                                            {'name': 'applied', 'label': 'Applied On', 'field': 'applied'},
                                            {'name': 'status', 'label': 'Status', 'field': 'status'},
                                        ]
                                        rows = [
                                            {
                                                'request': a.request_id,
                                                'applied':  str(a.applied_at)[:10],
                                                'status':  a.status.value.upper(),
                                            }
                                            for a in my_apps
                                        ]
                                        ui.table(columns=columns, rows=rows).classes('w-full')

                            db.close()












