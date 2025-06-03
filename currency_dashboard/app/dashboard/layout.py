import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from app.db import SessionLocal
from app.db.models import Currency, CurrencyPair


def get_currency_options():
    session = SessionLocal()
    try:
        currencies = session.query(Currency).all()
        return [{"label": c.code, "value": c.code} for c in currencies]
    finally:
        session.close()


def get_currency_pair_options():
    session = SessionLocal()
    try:
        pairs = session.query(CurrencyPair).all()
        return [
            {
                "label": f"{pair.base_currency} → {pair.target_currency}",
                "value": str(pair.id)
            }
            for pair in pairs
        ]
    finally:
        session.close()


def build_layout():
    """Макет для страницы курсов валют"""
    return html.Div([
        dbc.Container([
            dbc.Card([
                dbc.CardHeader("Добавить валютную пару"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Базовая валюта"),
                            dcc.Dropdown(id="base-currency", options=get_currency_options(), placeholder="USD")
                        ]),
                        dbc.Col([
                            html.Label("Целевая валюта"),
                            dcc.Dropdown(id="target-currency", options=get_currency_options(), placeholder="EUR")
                        ]),
                        dbc.Col([
                            html.Label(" "),
                            html.Button("Добавить", id="add-pair-btn", className="btn btn-primary w-100")
                        ])
                    ]),
                    html.Div(id="add-pair-msg", className="mt-2 text-success")
                ])
            ], className="mb-4"),

            dbc.Card([
                dbc.CardHeader("Анализ курсов"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Валютная пара"),
                            dcc.Dropdown(
                                id="pair-dropdown",
                                options=get_currency_pair_options(),
                                placeholder="Выберите пару"
                            )
                        ]),
                        dbc.Col([
                            html.Label("Режим"),
                            dcc.RadioItems(
                                id="mode-toggle",
                                options=[
                                    {"label": "Live", "value": "live"},
                                    {"label": "История", "value": "history"}
                                ],
                                value="history",
                                labelStyle={"marginRight": "10px"},
                                inline=True
                            )
                        ])
                    ])
                ])
            ], className="mb-4"),

            html.Div(id="history-container", children=[
                dbc.Card([
                    dbc.CardHeader("Выбор периода"),
                    dbc.CardBody([
                        dcc.DatePickerRange(id="date-range")
                    ])
                ], className="mb-3"),

                dcc.Graph(id="exchange-rate-graph"),

                html.H4("Таблица курсов", className="mt-4"),
                dash_table.DataTable(
                    id="rate-table",
                    columns=[
                        {"name": "Пара", "id": "pair"},
                        {"name": "Дата", "id": "date"},
                        {"name": "Курс", "id": "rate"}
                    ],
                    data=[],
                    page_size=10,
                    style_table={"overflowX": "auto"},
                    style_cell_conditional=[],
                    style_cell={"textAlign": "left"},
                    style_header={}
                ),

                html.H4("Экспорт таблицы", className="mt-4"),
                dbc.Row([
                    dbc.Col([
                        dcc.RadioItems(
                            id="export-format",
                            options=[
                                {"label": "CSV", "value": "csv"},
                                {"label": "Excel", "value": "xlsx"}
                            ],
                            value="csv",
                            inline=True
                        )
                    ], width=3),
                    dbc.Col([
                        html.Button("Скачать", id="download-btn", className="btn btn-success")
                    ], width=2)
                ]),
                dcc.Download(id="download-data")
            ]),

            html.Div(id="live-container", className="mt-4")
        ], fluid=True)
    ])

def get_main_layout():
    """Главный макет с навигацией и контентом страницы"""
    return html.Div(id="main-container", children=[
        # Navigation bar - fixed on all pages
        dbc.Navbar(
            dbc.Container([
                # Логотип и название
                dbc.NavbarBrand("Currency Dashboard", href="/", className="ms-2"),
                
                # Навигационное меню
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-chart-line me-1"), "📊 Курсы валют"
                    ], href="/", active="exact")),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-info-circle me-1"), "🌐 Справка по валютам"
                    ], href="/info", active="exact"))
                ], className="me-auto", navbar=True),
                
                # Переключатель темы
                dbc.NavItem(html.Div([
                    html.Span("Тема:", className="me-2 text-white"),
                    dbc.RadioItems(
                        id="theme-toggle",
                        options=[
                            {"label": "🌞", "value": "light"},
                            {"label": "🌙", "value": "dark"}
                        ],
                        value="light",
                        inline=True,
                        className="toggle-dark-mode",
                        inputClassName="form-check-input",
                        labelClassName="form-check-label",
                        labelCheckedClassName="active"
                    )
                ], className="d-flex align-items-center"))
            ], fluid=True),
            color="primary",
            dark=True,
            className="mb-4",
            fixed="top",
            style={"zIndex": "1030"}
        ),
        
        # URL location component
        dcc.Location(id="url", refresh=False),
        
        # Контент страницы с отступом для navbar
        html.Div(id="page-content", style={"paddingTop": "70px", "minHeight": "calc(100vh - 70px)"})
    ])
