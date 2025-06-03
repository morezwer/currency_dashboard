from dash import html, dcc
import dash_bootstrap_components as dbc
import requests
import pandas as pd


def get_layout():
    # Получаем все валюты
    try:
        resp = requests.get("https://api.frankfurter.app/currencies")
        currencies_data = resp.json()
        
        # Получаем базовые курсы относительно EUR
        rates_resp = requests.get("https://api.frankfurter.app/latest?from=EUR")
        rates_data = rates_resp.json()
        rates = rates_data.get('rates', {})
    except Exception as e:
        currencies_data = {}
        rates = {}
        error_message = html.Div(
            html.P(f"Ошибка при загрузке данных: {str(e)}"),
            className="alert alert-danger"
        )

    # Создаем таблицу валют с информацией о курсах
    currency_rows = []
    for code, name in sorted(currencies_data.items()):
        # Получаем курс относительно EUR
        rate = rates.get(code, "—")
        rate_str = f"{rate}" if rate != "—" else "—"
        
        # Добавляем строку с флагом страны
        flag_url = f"https://flagcdn.com/w40/{code[:2].lower()}.png"
        if code == "EUR":
            rate_str = "1.0"  # EUR to EUR is always 1.0
            
        currency_rows.append(
            html.Tr([
                html.Td([
                    html.Img(src=flag_url, width="25px", style={"marginRight": "10px"}),
                    html.Span(code)
                ]),
                html.Td(name),
                html.Td(rate_str)
            ])
        )

    return dbc.Container([
        # Хлебные крошки для навигации
        dbc.Breadcrumb(
            items=[
                {"label": "Главная", "href": "/", "external_link": True},
                {"label": "Справка по валютам", "active": True},
            ],
            className="mt-2 mb-3"
        ),
        
        # Заголовок и описание
        html.H2("🌐 Справка по валютам", className="mt-2 mb-4"),
        
        dbc.Card([
            dbc.CardBody([
                html.P([
                    "Данное приложение использует данные из ",
                    html.A("Frankfurter API", href="https://www.frankfurter.app/", target="_blank"),
                    " — бесплатного API для получения исторических и актуальных курсов валют, публикуемых Европейским центральным банком."
                ]),
                html.P("Обновление курсов происходит каждый рабочий день около 16:00 CET.")
            ])
        ], className="mb-4"),
        
        html.H4("Поддерживаемые валюты"),
        html.P("Ниже представлен список всех валют, поддерживаемых API, с текущими курсами относительно EUR:"),
        
        # Таблица валют
        dbc.Table(
            # Header
            [html.Thead(html.Tr([
                html.Th("Код"), 
                html.Th("Название"), 
                html.Th("Курс к EUR")
            ]))] + 
            # Body
            [html.Tbody(currency_rows)],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            className="mt-3",
            id="info-table"
        ),
        
        # Инструкция по добавлению валютной пары
        html.H4("Как добавить новую валютную пару?", className="mt-5"),
        dbc.Card([
            dbc.CardBody([
                html.P("Для добавления новой валютной пары для отслеживания:"),
                html.Ol([
                    html.Li("Перейдите на вкладку «Курсы валют»"),
                    html.Li("В разделе «Добавить валютную пару» выберите базовую и целевую валюты"),
                    html.Li("Нажмите кнопку «Добавить»"),
                    html.Li("После добавления пара появится в выпадающем списке «Валютная пара»")
                ]),
                html.P("Приложение автоматически начнет собирать актуальные данные по добавленной паре.")
            ])
        ], className="mb-4"),
        
        # Полезные ссылки
        html.H4("Полезные ссылки", className="mt-4"),
        dbc.ListGroup([
            dbc.ListGroupItem([
                html.A("Frankfurter API документация", href="https://www.frankfurter.app/docs/", target="_blank")
            ]),
            dbc.ListGroupItem([
                html.A("Европейский центральный банк - Курсы валют", href="https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/", target="_blank")
            ])
        ], className="mb-5"),
        
        # Кнопка возврата на главную страницу
        dbc.Button([
            "← Вернуться к курсам валют"
        ], href="/", color="primary", className="mt-4 mb-5")
    ], fluid=True)
