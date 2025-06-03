import requests
from app.db import SessionLocal
from app.db.models import Source, Currency, CurrencyPair, ExchangeRate
from datetime import datetime


def fetch_exchange_rate(base: str, target: str):
    session = SessionLocal()
    try:
        # 1. Источник
        source_name = "frankfurter.app"
        source = session.query(Source).filter_by(name=source_name).first()
        if not source:
            source = Source(name=source_name, api_url="https://api.frankfurter.app")
            session.add(source)
            session.commit()

        # 2. Валюты
        for code in (base, target):
            if not session.query(Currency).filter_by(code=code).first():
                session.add(Currency(code=code, name=code))
        session.commit()

        # 3. Валютная пара
        pair = (
            session.query(CurrencyPair)
            .filter_by(base_currency=base, target_currency=target)
            .first()
        )
        if not pair:
            pair = CurrencyPair(base_currency=base, target_currency=target)
            session.add(pair)
            session.commit()

        # 4. Запрос к API
        url = f"https://api.frankfurter.app/latest?from={base}&to={target}"
        resp = requests.get(url)
        data = resp.json()

        if "rates" not in data or target not in data["rates"]:
            print("Ошибка получения курса:", data)
            return

        rate = data["rates"][target]
        timestamp = datetime.strptime(data["date"], "%Y-%m-%d")

        # 5. Сохранение
        record = ExchangeRate(
            pair_id=pair.id,
            source_id=source.id,
            timestamp=timestamp,
            rate=rate
        )
        session.add(record)
        session.commit()

        print(f"[OK] {base}->{target}: {rate} на {timestamp.date()}")

    except Exception as e:
        session.rollback()
        print("Ошибка при получении курса:", str(e))

    finally:
        session.close()
