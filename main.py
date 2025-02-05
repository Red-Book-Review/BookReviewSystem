import datetime
from database import Session, Review, create_tables, login_editor, register_editor

# Функция для получения числового значения в заданном диапазоне
def get_float(prompt, min_val=0, max_val=20):
    while True:
        try:
            value = float(input(prompt).strip())
            if min_val <= value <= max_val:
                return value
            print(f"Введите число в диапазоне {min_val}-{max_val}.")
        except ValueError:
            print("❌ Ошибка ввода. Введите число.")

# Ввод оценки книги
def input_review(editor_username):
    print("\n📖 Оценка произведения")
    title = input("Название книги: ")
    author = input("Автор: ")
    genre = input("Жанр (фантастика, детектив, романтика и т.д.): ").strip().lower()

    # Ввод оценок
    idea = get_float("Оценка \"Идея и оригинальность\": ")
    style = get_float("Оценка \"Повествование и стиль\": ")
    plot = get_float("Оценка \"Целостность сюжета\": ")
    emotion = get_float("Оценка \"Эмоциональный отклик\": ")
    influence = get_float("Оценка \"Влияние произведения\" (бонус): ", min_val=0)

    # Рассчёт итоговой оценки
    final_score = (idea + style + plot + emotion + influence) / 5 * 5

    print(f"\n📊 Итоговая оценка: {final_score:.2f}/100")
    confirm = input("Сохранить в базу данных? (y/n): ").strip().lower()

    if confirm == "y":
        session = Session()
        new_review = Review(
            title=title, author=author, evaluator=editor_username, genre=genre,
            idea=idea, style=style, plot=plot, emotion=emotion, influence=influence,
            final_score=final_score, review_date=datetime.date.today()
        )
        session.add(new_review)
        session.commit()
        session.close()
        print("✅ Оценка сохранена.")
    else:
        print("❌ Отмена сохранения.")

# Главная программа
if __name__ == "__main__":
    create_tables()

    print("\n🔹 Добро пожаловать в систему оценки книг 🔹")
    print("1. Войти в систему")
    print("2. Зарегистрировать нового редактора")
    
    choice = input("Выберите действие: ").strip()
    if choice == "2":
        register_editor()
    elif choice == "1":
        editor = login_editor()
        if editor:
            input_review(editor)
