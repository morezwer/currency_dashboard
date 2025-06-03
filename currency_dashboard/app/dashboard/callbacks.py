from dash import Input, Output, State, html, dcc
import plotly.graph_objects as go
import requests
import pandas as pd
from app.db import SessionLocal
from app.db.models import ExchangeRate, CurrencyPair
from datetime import datetime
from app.dashboard.layout import get_currency_pair_options
import dash_bootstrap_components as dbc
import dash


def register_callbacks(app):
    @app.callback(
        Output("exchange-rate-graph", "figure"),
        Output("rate-table", "data"),
        Input("pair-dropdown", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("mode-toggle", "value"),
        Input("theme-toggle", "value")
    )
    def update_graph_and_table(pair_id, start_date, end_date, mode, theme):
        if mode != "history" or not pair_id:
            # Возвращаем пустой график с правильной темой
            empty_fig = go.Figure()
            if theme == "dark":
                empty_fig.update_layout(
                    template="plotly_dark",
                    plot_bgcolor="#1E1E1E",
                    paper_bgcolor="#121212",
                    font=dict(color="#E0E0E0")
                )
            return empty_fig, []

        session = SessionLocal()
        try:
            pair = session.query(CurrencyPair).filter_by(id=int(pair_id)).first()
            if not pair:
                # Пустой график с правильной темой
                empty_fig = go.Figure()
                if theme == "dark":
                    empty_fig.update_layout(
                        title="Пара не найдена",
                        template="plotly_dark",
                        plot_bgcolor="#1E1E1E",
                        paper_bgcolor="#121212",
                        font=dict(color="#E0E0E0")
                    )
                else:
                    empty_fig.update_layout(title="Пара не найдена")
                return empty_fig, []
            base = pair.base_currency
            target = pair.target_currency
        finally:
            session.close()

        if not start_date or not end_date:
            # Пустой график с правильной темой
            empty_fig = go.Figure()
            if theme == "dark":
                empty_fig.update_layout(
                    title="Выберите диапазон дат",
                    template="plotly_dark",
                    plot_bgcolor="#1E1E1E",
                    paper_bgcolor="#121212",
                    font=dict(color="#E0E0E0")
                )
            else:
                empty_fig.update_layout(title="Выберите диапазон дат")
            return empty_fig, []

        url = f"https://api.frankfurter.app/{start_date}..{end_date}?from={base}&to={target}"
        try:
            response = requests.get(url)
            data = response.json()

            if "rates" not in data:
                # Пустой график с правильной темой
                empty_fig = go.Figure()
                if theme == "dark":
                    empty_fig.update_layout(
                        title="Нет данных от API",
                        template="plotly_dark",
                        plot_bgcolor="#1E1E1E",
                        paper_bgcolor="#121212",
                        font=dict(color="#E0E0E0")
                    )
                else:
                    empty_fig.update_layout(title="Нет данных от API")
                return empty_fig, []

            rates_dict = data["rates"]
            dates = sorted(rates_dict.keys())
            rates = [rates_dict[d][target] for d in dates]

            fig = go.Figure()
            
            # Улучшенный стиль графика в зависимости от темы
            if theme == "dark":
                line_color = "#8AB4F8"  # Голубой для темной темы
                marker_color = "#4285F4"  # Google синий
                fig.add_trace(go.Scatter(
                    x=dates, 
                    y=rates, 
                    mode="lines+markers",
                    line=dict(color=line_color, width=2),
                    marker=dict(color=marker_color, size=8)
                ))
                fig.update_layout(
                    title=f"{base} → {target}",
                    xaxis_title="Дата",
                    yaxis_title="Курс",
                    template="plotly_dark",
                    plot_bgcolor="#1E1E1E",
                    paper_bgcolor="#121212",
                    font=dict(color="#E0E0E0")
                )
            else:
                # Светлая тема
                line_color = "#1A73E8"  # Google синий для светлой темы
                marker_color = "#0F4BAA"  # Темный синий
                fig.add_trace(go.Scatter(
                    x=dates, 
                    y=rates, 
                    mode="lines+markers",
                    line=dict(color=line_color, width=2),
                    marker=dict(color=marker_color, size=8)
                ))
                fig.update_layout(
                    title=f"{base} → {target}",
                    xaxis_title="Дата",
                    yaxis_title="Курс",
                    template="plotly_white"
                )

            table_data = [
                {"pair": f"{base} → {target}", "date": d, "rate": rates_dict[d][target]}
                for d in dates
            ]

            return fig, table_data

        except Exception as e:
            # Пустой график с правильной темой
            empty_fig = go.Figure()
            if theme == "dark":
                empty_fig.update_layout(
                    title=f"Ошибка API: {e}",
                    template="plotly_dark",
                    plot_bgcolor="#1E1E1E",
                    paper_bgcolor="#121212",
                    font=dict(color="#E0E0E0")
                )
            else:
                empty_fig.update_layout(title=f"Ошибка API: {e}")
            return empty_fig, []

    @app.callback(
        Output("add-pair-msg", "children"),
        Output("pair-dropdown", "options"),
        Input("add-pair-btn", "n_clicks"),
        State("base-currency", "value"),
        State("target-currency", "value"),
        prevent_initial_call=True
    )
    def add_currency_pair(n_clicks, base, target):
        if not base or not target:
            return "Выберите обе валюты", get_currency_pair_options()

        if base == target:
            return "Валюты не должны совпадать", get_currency_pair_options()

        session = SessionLocal()
        try:
            exists = (
                session.query(CurrencyPair)
                .filter_by(base_currency=base, target_currency=target)
                .first()
            )
            if exists:
                return "Пара уже существует", get_currency_pair_options()

            pair = CurrencyPair(base_currency=base, target_currency=target)
            session.add(pair)
            session.commit()
            return "Пара добавлена!", get_currency_pair_options()

        except Exception as e:
            session.rollback()
            return f"Ошибка: {str(e)}", get_currency_pair_options()

        finally:
            session.close()

    @app.callback(
        Output("history-container", "style"),
        Output("live-container", "children"),
        Input("mode-toggle", "value"),
        Input("pair-dropdown", "value"),
        Input("theme-toggle", "value")
    )
    def toggle_mode_display(mode, pair_id, theme):
        if mode == "history":
            return {"display": "block"}, ""

        if not pair_id:
            return {"display": "none"}, html.P("Выберите валютную пару.")

        session = SessionLocal()
        try:
            rate = (
                session.query(ExchangeRate)
                .filter_by(pair_id=int(pair_id))
                .order_by(ExchangeRate.timestamp.desc())
                .first()
            )
            if not rate:
                return {"display": "none"}, html.P("Нет данных для выбранной пары.")

            card_style = {}
            if theme == "dark":
                card_style = {
                    "backgroundColor": "#1F1F1F", 
                    "borderColor": "#333", 
                    "color": "white",
                    "padding": "20px",
                    "borderRadius": "8px",
                    "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.3)"
                }

            return {"display": "none"}, html.Div([
                dbc.Card([
                    dbc.CardHeader(html.H3("Текущий курс", className="mb-0")),
                    dbc.CardBody([
                        html.P(f"Дата: {rate.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"),
                        html.H4(f"Курс: {rate.rate}", 
                                style={"color": "#8AB4F8" if theme == "dark" else "#1A73E8"})
                    ])
                ], style=card_style if theme == "dark" else {})
            ])
        finally:
            session.close()

    @app.callback(
        Output("download-data", "data"),
        Input("download-btn", "n_clicks"),
        State("rate-table", "data"),
        State("export-format", "value"),
        prevent_initial_call=True
    )
    def export_table(n_clicks, table_data, file_format):
        if not table_data:
            return None

        df = pd.DataFrame(table_data)

        if file_format == "csv":
            return dcc.send_data_frame(df.to_csv, filename="exchange_rates.csv", index=False)
        else:
            return dcc.send_data_frame(df.to_excel, filename="exchange_rates.xlsx", index=False)

    @app.callback(
    Output("main-container", "style"),
    Output("main-container", "className"),
    Input("theme-toggle", "value"),
    Input("url", "pathname")
    )
    def update_theme_styles(theme, pathname):
        if theme == "dark":
            return (
                # Main container style
                {
                    "backgroundColor": "#121212",
                    "color": "white",
                    "minHeight": "100vh",
                    "padding": "15px",
                    "transition": "all 0.3s ease"
                },
                # Class name for dark theme
                "dark-theme"
            )
        else:
            return (
                # Main container style
                {
                    "backgroundColor": "white",
                    "color": "black",
                    "minHeight": "100vh",
                    "padding": "15px",
                    "transition": "all 0.3s ease"
                },
                # Class name for light theme
                ""
            )
            
    # Отдельный callback для стилей таблицы, который выполняется только на главной странице
    @app.callback(
        Output("rate-table", "style_header", allow_duplicate=True),
        Output("rate-table", "style_cell", allow_duplicate=True),
        Output("rate-table", "style_data", allow_duplicate=True),
        Output("rate-table", "style_data_conditional", allow_duplicate=True),
        Input("theme-toggle", "value"),
        Input("url", "pathname"),
        prevent_initial_call=True
    )
    def update_table_styles(theme, pathname):
        # Проверяем, что мы на главной странице, где есть таблица
        if pathname != "/info":
            if theme == "dark":
                return (
                    # Table header style
                    {
                        "backgroundColor": "#333333",
                        "color": "white",
                        "fontWeight": "bold",
                        "border": "1px solid #444"
                    },
                    # Table cell style
                    {
                        "backgroundColor": "#1e1e1e",
                        "color": "white",
                        "textAlign": "left",
                        "border": "1px solid #333",
                        "fontFamily": "'Segoe UI', Roboto, sans-serif"
                    },
                    # Table data style
                    {
                        "backgroundColor": "#252525"
                    },
                    # Conditional row styling
                    [
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#1a1a1a"
                        }
                    ]
                )
            else:
                return (
                    # Table header style
                    {
                        "backgroundColor": "#4285F4",
                        "color": "white",
                        "fontWeight": "bold"
                    },
                    # Table cell style
                    {
                        "backgroundColor": "white",
                        "color": "black",
                        "textAlign": "left",
                        "fontFamily": "'Segoe UI', Roboto, sans-serif"
                    },
                    # Table data style
                    {
                        "backgroundColor": "white"
                    },
                    # Conditional row styling
                    [
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#f9f9f9"
                        }
                    ]
                )
        # На странице справки не обновляем стили таблицы
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
    # Callback для стилей таблицы на странице информации
    @app.callback(
        Output("info-table", "className"),
        Input("theme-toggle", "value"),
        Input("url", "pathname"),
        prevent_initial_call=True
    )
    def update_info_table_styles(theme, pathname):
        if pathname == "/info":
            base_class = "mt-3 table-bordered table-hover table-responsive table-striped"
            if theme == "dark":
                return f"{base_class} table-dark"
            else:
                return base_class
        return dash.no_update
    
    # Добавляем callback для обработки URL и переключения страниц
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname")
    )
    def display_page(pathname):
        if pathname == "/info":
            from app.dashboard.pages.info import get_layout
            return get_layout()
        else:
            from app.dashboard.pages.dashboard import get_layout
            return get_layout()
