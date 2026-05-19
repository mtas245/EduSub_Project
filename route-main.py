# main.py - add alongside existing routes
from views.profile import profile_view


@ui.page("/profile")
def profile_page():
    if not app.storage.user.get("logged_in"):
        ui.navigate.to("/login")
        return
    profile_view()
