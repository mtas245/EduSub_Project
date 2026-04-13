from nicegui import ui, app
from database import SessionLocal
from services.request_service import RequestService
from services.application_service import ApplicationService
from datetime import datetime

def teacher_dashboard_view():
    db = SessionLocal()
    req_service = RequestService(db)
    app_service = ApplicationService(db)
    teacher_id = app.storage.user.get('user_id')

    with ui.column().classes('w-full max-w-4xl mx-auto p-6'):

        # Header
        with ui.row().classes('w-full items-center justify-between mb-6'):
            ui.label('Available Assignments').classes('text-3xl font-bold')
            with ui.row().classes('gap-2'):
                ui.button('My Profile',
                    on_click=lambda: ui.navigate.to('/profile')
                ).classes('bg-blue-100')
                ui.button('Logout', on_click=lambda: (
                    app.storage.user.clear(),
                    ui.navigate.to('/')
                ))

        # Grade filter
        grade_filter = ui.select(
            label='Educational Level',
            options=['All', 'KG', 'Primary'],
            value='All'
        ).classes('w-64 mb-4')

        now = datetime.now()
        valid = [r for r in req_service.get_open_requests()
                 if r.expires_at is None or r.expires_at > now]
        
        container = ui.column().classes('w-full')

        def render():
            container.clear()
            level = grade_filter.value
            filtered = valid

            if level == 'KG':
                filtered = [r for r in valid if r.grade_level in ('KG1', 'KG2')]

            elif level == 'Primary':
                filtered = [r for r in valid if r.grade_level not in ('KG1', 'KG2')]

            with container:
                if not filtered:
                    ui.label('No open assignments.').classes('text-gray-400')
                    return

                for req in filtered:
                    with ui.card().classes('w-full p-4 mb-3'):
                        with ui.row().classes('w-full justify-between items-center'):
                            with ui.column():
                                ui.label(
                                    f'{req.grade_level} - {req.subject}'
                                ).classes('font-bold text-lg')
                                ui.label(
                                    f'Date: {req.date.strftime("%Y-%m-%d")}'
                                ).classes('text-gray-600')
                                ui.label(
                                    f'Time: {req.time_slot}' if req.time_slot else 'Time: not specified'
                                ).classes('text-gray-500')
                                if req.expires_at:
                                    hours = int(
                                        (req.expires_at - datetime.now()).total_seconds() // 3600
                                    )
                                    col = 'text-red-500' if hours < 6 else 'text-gray-400'
                                    ui.label(f'Expires in {hours}h').classes(col)

                            def make_apply(rid=req.id):
                                def apply():
                                    result = app_service.apply(
                                        teacher_id=teacher_id, 
                                        request_id=rid
                                    )
                                    ui.notify(result['message'])
                                    render()
                                return apply
                            
                            ui.button('Apply', on_click=make_apply())

        grade_filter.on('update:model-value', lambda _: render())
        render()
    
    db.close()



                                      