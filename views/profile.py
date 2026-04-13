# views/profile.py
from nicegui import ui, app
from database import SessionLocal
from services.profile_service import ProfileService


def profile_view():
    db = SessionLocal()
    service = ProfileService(db)
    user_id = app.storage.user.get("user_id")
    user = service.get_profile(user_id)

    if not user:
        ui.navigate.to("/login")
        return

    with ui.column().classes("w-full max-w-2xl mx-auto p-6"):
        with ui.row().classes("w-full item-center justify-between mb-6"):
            ui.label("My Profile").classes("text-3xl font-bold")
            ui.button("Back", on_click=lambda: ui.navigate.to("/teacher"))

        # Staff number('Back', on_click=labda: ui.navigate.to('/teacher'))
        with ui.card().classes("w-full p-4 mb-4 bg-blue-50"):
            ui.label("Your Staff Number").classes("text-xs text-gray-500")
            ui.label(user.personal_number or "Not assigned yet").classes(
                "text-2xl font-mono font-bold text-blue-700"
            )
            ui.label("Used by admins to identify you.").classes("text-xs text-gray-400")

        # Editable fields
        with ui.card().classes("w-full p-6"):
            ui.label("Edit Profile").classes("text-xl font-bold mb-4")

            name_input = ui.input("Full Name", value=user.full_name or "").classes(
                "w-full"
            )
            ui.input("Email (cannot be changed)", value=user.email or "").classes(
                "w-full"
            ).props("readonly")
            phone_input = ui.input("Phone", value=user.phone or "").classes("w-full")
            subjects_input = ui.input(
                "Subjects (e.g. German, Mathematics, PE", value=user.subjects or ""
            ).classes("w-full")
            bio_input = ui.textarea("Short bio", value=user.bio or "").classes("w-full")
        success_label = ui.label("").classes("text-green-600")

        def save():
            service.update_profile(
                user_id=user_id,
                full_name=name_input.value,
                phone=phone_input.value,
                subjects=subjects_input.value,
                bio=bio_input.value,
            )


    ui.button("Save", on_click=save).classes("w-full mt-4")
