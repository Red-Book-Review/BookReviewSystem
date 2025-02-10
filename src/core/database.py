import os, datetime, bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Загружаем переменные окружения
load_dotenv()
DATABASE_URL = os.getenv("DB_EXTERNAL_DATABASE_URL", "sqlite:///reviews.db")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

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
    idea_reason = Column(String(500))
    style_reason = Column(String(500))
    plot_reason = Column(String(500))
    emotion_reason = Column(String(500))
    influence_reason = Column(String(500))

class DeletedReview(Base):
    __tablename__ = "deleted_reviews"
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer)
    deletion_reason = Column(Integer, nullable=True)
    deletion_date = Column(Date, default=datetime.date.today)

def create_tables():
    Base.metadata.create_all(engine)

def login_editor(username, password):
    session = Session()
    editor = session.query(Editor).filter_by(username=username).first()
    result = editor and bcrypt.checkpw(password.encode(), editor.password_hash.encode())
    session.close()
    return result

# Экспортируем все нужные элементы
__all__ = ['Session', 'Base', 'Editor', 'Review', 'DeletedReview', 
           'create_tables', 'login_editor']
