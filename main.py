import datetime
import sqlite3
import matplotlib.pyplot as plt

def get_float(prompt, default=None, min_val=0, max_val=20):
    """Получает число с плавающей запятой от пользователя, ограниченное диапазоном."""
    while True:
        try:
            s = input(prompt).strip()
            if not s and default is not None:
                return default
            value = float(s)
            if min_val <= value <= max_val:
                return value
            print(f"Введите число в диапазоне от {min_val} до {max_val}.")
        except ValueError:
            print("Введите корректное число.")

def setup_database():
    """Создает таблицу для хранения оценок, если её нет."""
    conn = sqlite3.connect("book_reviews.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            evaluator TEXT,
            genre TEXT,
            idea INTEGER,
            style INTEGER,
            plot INTEGER,
            emotion INTEGER,
            influence INTEGER,
            score REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_review(title, author, evaluator, genre, scores, final_score):
    """Сохраняет результаты оценки в базу данных."""
    conn = sqlite3.connect("book_reviews.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reviews (title, author, evaluator, genre, idea, style, plot, emotion, influence, score, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, author, evaluator, genre, scores["idea"], scores["style"], scores["plot"], scores["emotion"], scores["influence"], final_score, datetime.datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

def plot_results(scores):
    """Создает диаграмму с оценками книги."""
    labels = ["Идея", "Стиль", "Сюжет", "Эмоции", "Влияние"]
    values = [scores["idea"], scores["style"], scores["plot"], scores["emotion"], scores["influence"]]
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color=['blue', 'green', 'red', 'purple', 'orange'])
    plt.ylim(0, 20)
    plt.title("Оценка книги по критериям")
    plt.xlabel("Критерии")
    plt.ylabel("Баллы")
    plt.show()

def calculate_score():
    print("Система оценки произведения (каждый критерий от 0 до 20 баллов)")
    setup_database()
    
    title = input("Введите название книги: ")
    author = input("Введите автора книги: ")
    evaluator = input("Введите ваше имя (оценщик): ")
    
    genres = {
        "фантастика": {"idea": 0.35, "style": 0.25, "plot": 0.20, "emotion": 0.20, "influence": 0.10},
        "детектив": {"idea": 0.20, "style": 0.25, "plot": 0.40, "emotion": 0.15, "influence": 0.10},
        "романтика": {"idea": 0.15, "style": 0.30, "plot": 0.25, "emotion": 0.30, "influence": 0.10},
        "поэзия": {"idea": 0.10, "style": 0.35, "plot": 0.15, "emotion": 0.40, "influence": 0.10},
        "научная литература": {"idea": 0.25, "style": 0.20, "plot": 0.30, "emotion": 0.15, "influence": 0.10},
        "безжанровый": {"idea": 0.25, "style": 0.25, "plot": 0.25, "emotion": 0.25, "influence": 0.10}
    }
    
    genre = input("Введите жанр книги (или 'безжанровый'): ").lower()
    while genre not in genres:
        print("Некорректный жанр. Попробуйте снова.")
        genre = input("Введите жанр книги (или 'безжанровый'): ").lower()
    
    weights = genres[genre]
    scores = {}
    for key, label in zip(["idea", "style", "plot", "emotion", "influence"],
                           ["Идея и оригинальность", "Повествование и стиль", "Целостность сюжета", "Эмоциональный отклик", "Влияние"]):
        scores[key] = get_float(f"Введите оценку \"{label}\" (0-20): ")
    
    base_score = sum((scores[k] / 20) * weights[k] for k in ["idea", "style", "plot", "emotion"])
    bonus = (scores["influence"] / 20) * weights["influence"]
    final_score = (base_score + bonus) * 100
    
    print("\nРезультаты оценки:")
    print(f"Название книги: {title}")
    print(f"Автор: {author}")
    print(f"Оценщик: {evaluator}")
    print(f"Жанр: {genre}")
    print(f"Базовая оценка: {base_score:.3f}")
    print(f"Бонус за влияние: {bonus:.3f}")
    print(f"Итоговая оценка (из 100): {final_score:.1f}")
    
    save_review(title, author, evaluator, genre, scores, final_score)
    plot_results(scores)
    
    print("\nЭтот код был разработан и обновлён мной.")
    print(f"Дата последнего изменения: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")

if __name__ == "__main__":
    calculate_score()
