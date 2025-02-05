import os
import datetime
import bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker

# Загружаем переменные окружения
load_dotenv()
DATABASE_URL = os.getenv("DB_EXTERNAL_DATABASE_URL")  # Используем внешний URL

print("Текущая директория:", os.getcwd())  # Проверяем, где ищем .env

load_dotenv()  # Загружаем переменные из .env

DATABASE_URL = os.getenv("DB_EXTERNAL_DATABASE_URL")  # Загружаем URL базы данных
print("Загруженный DATABASE_URL:", DATABASE_URL)  # Проверяем, загружены ли данные

if not DATABASE_URL:
    print("❌ Ошибка: DATABASE_URL не найден. Проверьте .env файл.")
    exit(1)

# Создаём подключение к БД
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Определяем таблицы
class Editor(Base):
    __tablename__ = "editors"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    author = Column(String(200))
    evaluator = Column(String(50))
    genre = Column(String(50))
    idea = Column(Integer)
    style = Column(Integer)
    plot = Column(Integer)
    emotion = Column(Integer)
    influence = Column(Integer)
    final_score = Column(Float)
    review_date = Column(Date)

# Функция создания таблиц
def create_tables():
    Base.metadata.create_all(engine)

# Регистрация нового редактора
def register_editor():
    session = Session()
    username = input("Введите новый логин: ").strip()
    password = input("Введите новый пароль: ").strip()
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_editor = Editor(username=username, password_hash=password_hash)
    session.add(new_editor)
    try:
        session.commit()
        print("✅ Редактор зарегистрирован.")
    except Exception as e:
        session.rollback()
        print("❌ Ошибка регистрации:", e)
    session.close()

# Вход редактора
def login_editor():
    session = Session()
    username = input("Введите логин: ").strip()
    password = input("Введите пароль: ").strip()
    editor = session.query(Editor).filter_by(username=username).first()
    session.close()
    if editor and bcrypt.checkpw(password.encode(), editor.password_hash.encode()):
        print("✅ Успешный вход.")
        return username
    else:
        print("❌ Неверный логин или пароль.")
        return None
