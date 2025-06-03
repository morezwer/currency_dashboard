from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import SQLALCHEMY_DATABASE_URL

# Создаем MySQL движок с connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    future=True,
    pool_recycle=3600,  # Переподключение к серверу каждый час
    pool_pre_ping=True  # Проверка, что соединение активно, перед тем как его использовать
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()
