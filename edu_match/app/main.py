from nicegui import ui
@ui.page('/')
def home():
    ui.label('EduMatch Platform')
    ui.label('System is running.')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

from app.infrastructure.db.database import Base, engine
from app.domain.models.user import User

Base.metadata.create_all(bind=engine)
