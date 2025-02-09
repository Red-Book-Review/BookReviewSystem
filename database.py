import os
import datetime
import bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Загружаем переменные окружения
load_dotenv()
DATABASE_URL = os.getenv("DB_EXTERNAL_DATABASE_URL")

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
    # Новые поля для сохранения причины оценки каждого критерия
    idea_reason = Column(String(500))
    style_reason = Column(String(500))
    plot_reason = Column(String(500))
    emotion_reason = Column(String(500))
    influence_reason = Column(String(500))

# Функция создания таблиц
def create_tables():
    Base.metadata.create_all(engine)
    migrate_reviews_table()  # Добавляем вызов миграции после создания таблиц

# Функция для миграции таблицы reviews (если уже существует)
def migrate_reviews_table():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS idea_reason VARCHAR(500);"))
        conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS style_reason VARCHAR(500);"))
        conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS plot_reason VARCHAR(500);"))
        conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS emotion_reason VARCHAR(500);"))
        conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS influence_reason VARCHAR(500);"))
        conn.commit()

# Просмотр всех отзывов
def view_reviews():
    session = Session()
    reviews = session.query(Review).all()
    if not reviews:
        print("❌ Нет сохранённых оценок.")
    else:
        for review in reviews:
            print(f"\n📖 {review.title} ({review.author}) - {review.genre}")
            print(f"Оценка: {review.final_score}/100")
            print(f"Оценил: {review.evaluator} | Дата: {review.review_date}")
    session.close()

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
def login_editor(username, password):
    session = Session()
    editor = session.query(Editor).filter_by(username=username).first()
    if editor and bcrypt.checkpw(password.encode(), editor.password_hash.encode()):
        session.close()
        return True
    session.close()
    return False
