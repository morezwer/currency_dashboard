import requests
from app.db import SessionLocal
from app.db.models import Currency


def populate_currencies_from_api():
    url = "https://api.frankfurter.app/currencies"
    response = requests.get(url)
    data = response.json()

    session = SessionLocal()
    try:
        for code, name in data.items():
            exists = session.query(Currency).filter_by(code=code).first()
            if not exists:
                session.add(Currency(code=code, name=name))
        session.commit()
        print(f"[INFO] Добавлены {len(data)} валют в базу.")
    except Exception as e:
        session.rollback()
        print("Ошибка при добавлении валют:", str(e))
    finally:
        session.close()
