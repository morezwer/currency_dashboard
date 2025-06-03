from app.db import Base, engine
from app.scheduler import start_scheduler
from app.dashboard.layout import get_main_layout
from app.dashboard.callbacks import register_callbacks
from app.db.init_data import populate_currencies_from_api
import dash_bootstrap_components as dbc
from dash import Dash
from sqlalchemy_utils import database_exists, create_database

# Создание БД, если она не существует
if not database_exists(engine.url):
    create_database(engine.url)

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)
populate_currencies_from_api()

# Запуск планировщика (обновление курсов по расписанию)
start_scheduler()

# Инициализация Dash приложения
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True  # Включаем для multipage
)
server = app.server

# Используем главный layout с системой роутинга
app.layout = get_main_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
