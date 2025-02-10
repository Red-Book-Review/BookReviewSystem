import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
DB_DATABASE_URL = os.environ.get("DB_EXTERNAL_DATABASE_URL", "sqlite:///reviews.db")
engine = create_engine(DB_DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

def create_tables():
    from . import models  # относительный импорт моделей
    Base.metadata.create_all(engine)
    migrate_reviews_table()

def migrate_reviews_table():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS idea_reason VARCHAR(500);"))
        conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS style_reason VARCHAR(500);"))
        conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS plot_reason VARCHAR(500);"))
        conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS emotion_reason VARCHAR(500);"))
        conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS influence_reason VARCHAR(500);"))
        conn.commit()
