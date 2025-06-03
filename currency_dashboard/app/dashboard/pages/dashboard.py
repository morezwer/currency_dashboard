from app.dashboard.layout import build_layout
import dash_bootstrap_components as dbc
from dash import html

def get_layout():
    """Создает макет главной страницы с курсами валют"""
    # Включаем хлебные крошки для главной страницы
    breadcrumbs = dbc.Breadcrumb(
        items=[
            {"label": "Главная", "href": "/", "active": True},
        ],
        className="mt-2 mb-3"
    )
    
    # Объединяем хлебные крошки с основным макетом
    return html.Div([
        breadcrumbs,
        build_layout()
    ])
