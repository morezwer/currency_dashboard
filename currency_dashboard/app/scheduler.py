from apscheduler.schedulers.background import BackgroundScheduler
import requests
from datetime import datetime
from app.db import SessionLocal
from app.db.models import CurrencyPair, Source, Currency, ExchangeRate


def fetch_and_save_all_pairs():
    session = SessionLocal()
    try:
        source_name = "frankfurter.app"
        source = session.query(Source).filter_by(name=source_name).first()
        if not source:
            source = Source(name=source_name, api_url="https://api.frankfurter.app")
            session.add(source)
            session.commit()

        pairs = session.query(CurrencyPair).all()
        for pair in pairs:
            base = pair.base_currency
            target = pair.target_currency

            url = f"https://api.frankfurter.app/latest?from={base}&to={target}"
            response = requests.get(url)
            data = response.json()

            if "rates" not in data or target not in data["rates"]:
                print(f"[WARN] Нет курса для {base}->{target}")
                continue

            rate_value = data["rates"][target]
            timestamp = datetime.strptime(data["date"], "%Y-%m-%d")

            # Записываем в базу
            record = ExchangeRate(
                pair_id=pair.id,
                source_id=source.id,
                timestamp=timestamp,
                rate=rate_value
            )
            session.add(record)
            session.commit()

            print(f"[OK] {base}->{target}: {rate_value} на {timestamp.date()}")

    except Exception as e:
        session.rollback()
        print("Ошибка автосбора:", str(e))

    finally:
        session.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=fetch_and_save_all_pairs,
        trigger="interval",
        minutes=1,  # можно изменить на 60 для часового интервала
        id="fetch_all_pairs",
        replace_existing=True
    )
    scheduler.start()
    print("[INFO] Планировщик автосбора запущен")
