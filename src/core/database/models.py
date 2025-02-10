from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
import datetime

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
    idea = Column(Float)
    style = Column(Float)
    plot = Column(Float)
    emotion = Column(Float)
    influence = Column(Float)
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
