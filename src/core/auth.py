import bcrypt
from src.core.database.models import Editor, Review
from src.core.database.connection import Session

class AuthManager:
    def login(self, username, password):
        session = Session()
        editor = session.query(Editor).filter(Editor.username == username).first()
        if editor and bcrypt.checkpw(password.encode(), editor.password_hash.encode()):
            session.close()
            return True
        session.close()
        return False

    @staticmethod
    def calculate_final_score(idea, style, plot, emotion, influence, weights=None):
        if weights is None:
            weights = {"idea": 1.0, "style": 1.0, "plot": 1.0, "emotion": 1.0}
        base_score = (
            (idea * weights["idea"] +
             style * weights["style"] +
             plot * weights["plot"] +
             emotion * weights["emotion"]) /
            sum(weights.values())
        ) * 4.25
        min_score = min(idea, style, plot, emotion)
        penalty = (20 - min_score) * 0.75
        influence_bonus = (influence / 20) * 15
        return max(0, min(100, base_score - penalty + influence_bonus))

    def register(self, username, password):
        session = Session()
        if session.query(Editor).filter(Editor.username == username).first():
            session.close()
            raise ValueError("Логин занят.")
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_editor = Editor(username=username, password_hash=password_hash)
        session.add(new_editor)
        session.commit()
        session.close()

    def change_password(self, username, current_password, new_password):
        session = Session()
        editor = session.query(Editor).filter(Editor.username == username).first()
        if editor and bcrypt.checkpw(current_password.encode(), editor.password_hash.encode()):
            # Добавляем игнор для type checking
            editor.password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()  # type: ignore
            session.commit()
            session.close()
            return True
        session.close()
        return False

    def update_review(self, review_id, **kwargs):
        session = Session()
        review = session.query(Review).filter(Review.id == review_id).first()
        if not review:
            session.close()
            raise ValueError("Отзыв не найден.")
        for key, value in kwargs.items():
            if hasattr(review, key):
                setattr(review, key, value)
        session.commit()
        session.close()
