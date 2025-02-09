import time, sys
from database import Session, Review, Editor, create_tables, login_editor, register_editor, view_reviews
import datetime
import matplotlib.pyplot as plt
from formula import calculate_final_score  # импорт новой функции

# Коэффициенты для жанров по умолчанию
genre_weights = {
    "фантастика": {"idea": 0.35, "style": 0.20, "plot": 0.25, "emotion": 0.15, "influence": 0.05},
    "детектив": {"idea": 0.20, "style": 0.20, "plot": 0.40, "emotion": 0.10, "influence": 0.10},
    "романтика": {"idea": 0.15, "style": 0.25, "plot": 0.20, "emotion": 0.30, "influence": 0.10},
    "поэзия": {"idea": 0.10, "style": 0.30, "plot": 0.10, "emotion": 0.40, "influence": 0.10},
    "научная литература": {"idea": 0.25, "style": 0.20, "plot": 0.25, "emotion": 0.15, "influence": 0.15},
    "безжанровый": {}  # Здесь редактор укажет веса вручную
}

def save_review_to_file(title, author, evaluator, genre, idea, idea_reason, style, style_reason, plot, plot_reason, emotion, emotion_reason, influence, influence_reason, final_score):
    filename = f"{title.replace(' ', '_')}_review.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"📖 Оценка книги: {title}\n")
        file.write(f"Автор: {author}\n")
        file.write(f"Оценщик: {evaluator}\n")
        file.write(f"Жанр: {genre}\n\n")
        file.write(f"Идея и оригинальность: {idea}/20\n")
        file.write(f"  Причина: {idea_reason}\n\n")
        file.write(f"Повествование и стиль: {style}/20\n")
        file.write(f"  Причина: {style_reason}\n\n")
        file.write(f"Целостность сюжета: {plot}/20\n")
        file.write(f"  Причина: {plot_reason}\n\n")
        file.write(f"Эмоциональный отклик: {emotion}/20\n")
        file.write(f"  Причина: {emotion_reason}\n\n")
        file.write(f"Влияние произведения (бонус): {influence}/20\n")
        file.write(f"  Причина: {influence_reason}\n\n")
        file.write(f"📊 Итоговая оценка: {final_score:.2f}/100\n\n")
        file.write("Формула:\n")
        file.write("(Идея*W1 + Стиль*W2 + Сюжет*W3 + Эмоции*W4) * Penalty + (Влияние*W5), затем умножить на 5\n")
        file.write("Penalty = 1.0, если все оценки ≥ 10; иначе, 1.0 + ((ср. остальных – главная)/ср. остальных)*0.5\n")
    print(f"✅ Оценка сохранена в файл: {filename}")

def plot_review_scores(idea, style, plot, emotion, influence):
    labels = ["Идея", "Стиль", "Сюжет", "Эмоции", "Влияние"]
    values = [idea, style, plot, emotion, influence]
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color=["blue", "green", "red", "purple", "orange"])
    plt.ylim(0, 20)
    plt.title("Баллы по критериям")
    plt.xlabel("Критерии")
    plt.ylabel("Баллы")
    plt.show()

def edit_review():
    session = Session()
    review_id = input("Введите ID оценки для редактирования: ").strip()
    review = session.query(Review).filter_by(id=review_id).first()
    if not review:
        print("❌ Оценка не найдена.")
        session.close()
        return
    print(f"Текущие оценки: Идея: {review.idea}, Стиль: {review.style}, Сюжет: {review.plot}, Эмоции: {review.emotion}, Влияние: {review.influence}")
    review.idea = int(input("Новая оценка 'Идея и оригинальность': "))
    review.idea_reason = input("Новая причина оценки 'Идея и оригинальность': ").strip()
    review.style = int(input("Новая оценка 'Повествование и стиль': "))
    review.style_reason = input("Новая причина оценки 'Повествование и стиль': ").strip()
    review.plot = int(input("Новая оценка 'Целостность сюжета': "))
    review.plot_reason = input("Новая причина оценки 'Целостность сюжета': ").strip()
    review.emotion = int(input("Новая оценка 'Эмоциональный отклик': "))
    review.emotion_reason = input("Новая причина оценки 'Эмоциональный отклик': ").strip()
    review.influence = int(input("Новая оценка 'Влияние произведения' (бонус): "))
    review.influence_reason = input("Новая причина оценки 'Влияние произведения': ").strip()

    if review.genre != "безжанровый":
        weights = genre_weights.get(review.genre, {})
    else:
        weights = {}
        print("🔹 Безжанровый режим: укажите проценты для оценки (сумма должна быть 1.0)")
        weights["idea"] = float(input("Процент для 'Идея': "))
        weights["style"] = float(input("Процент для 'Стиль': "))
        weights["plot"] = float(input("Процент для 'Сюжет': "))
        weights["emotion"] = float(input("Процент для 'Эмоции': "))
        weights["influence"] = float(input("Процент для 'Влияние' (бонус): "))
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 1e-6:
            print("❌ Ошибка: сумма должна быть 1.0!")
            session.close()
            return

    # Используем новую функцию расчёта итоговой оценки
    review.final_score = calculate_final_score(review.idea, review.style,
                                               review.plot, review.emotion,
                                               review.influence, weights)
    session.commit()
    session.close()
    print("✅ Оценка успешно обновлена.")

def adaptive_review_check(genre, current_score, review_id):
    # Анализируем отзывы данного жанра
    session = Session()
    reviews = session.query(Review).filter(Review.genre == genre).all()
    count_reviews = len(reviews)
    if count_reviews < 100:
        session.close()
        return  # Адаптация не требуется
    avg_score = sum(r.final_score for r in reviews) / count_reviews
    session.close()
    # Если отклонение больше 15% от среднего, предлагаем обновление
    if abs(current_score - avg_score) > 0.15 * avg_score:
        choice = input(f"Средняя оценка по жанру '{genre}' составляет {avg_score:.2f}/100. "
                       f"Ваша оценка {current_score:.2f}/100 сильно отличается. Изменить оценку на рекомендуемую? (y/n): ").strip().lower()
        if choice == "y":
            # Обновляем оценку в базе
            session = Session()
            review = session.query(Review).filter_by(id=review_id).first()
            if review:
                review.final_score = avg_score
                session.commit()
                print(f"✅ Оценка обновлена на рекомендуемое значение {avg_score:.2f}/100.")
            session.close()

def write_review(username):
    session = Session()
    title = input("Название книги: ").strip()
    author = input("Автор: ").strip()
    genre = input("Жанр (например, фантастика, детектив, романтика, поэзия, научная литература, безжанровый): ").strip().lower()
    if genre not in genre_weights:
        print("❌ Неизвестный жанр. Безжанровый режим активирован.")
        genre = "безжанровый"
        weights = {}
        print("🔹 Укажите процентное соотношение важности критериев (сумма должна быть 1.0)")
        weights["idea"] = float(input("Процент для 'Идея и оригинальность': "))
        weights["style"] = float(input("Процент для 'Повествование и стиль': "))
        weights["plot"] = float(input("Процент для 'Целостность сюжета': "))
        weights["emotion"] = float(input("Процент для 'Эмоциональный отклик': "))
        weights["influence"] = float(input("Процент для 'Влияние произведения' (бонус): "))
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 1e-6:
            print("❌ Ошибка: сумма всех значений должна быть 1.0! Попробуйте снова.")
            session.close()
            return
    else:
        weights = genre_weights[genre]
    try:
        idea = int(input("Оценка 'Идея и оригинальность' (0-20): "))
        style = int(input("Оценка 'Повествование и стиль' (0-20): "))
        plot = int(input("Оценка 'Целостность сюжета' (0-20): "))
        emotion = int(input("Оценка 'Эмоциональный отклик' (0-20): "))
        influence = int(input("Оценка 'Влияние произведения' (бонус, 0-20): "))
    except ValueError:
        print("❌ Ошибка: введено не числовое значение. Попробуйте снова.")
        session.close()
        return
    idea_reason = input("Причина оценки 'Идея и оригинальность': ").strip()
    style_reason = input("Причина оценки 'Повествование и стиль': ").strip()
    plot_reason = input("Причина оценки 'Целостность сюжета': ").strip()
    emotion_reason = input("Причина оценки 'Эмоциональный отклик': ").strip()
    influence_reason = input("Причина оценки 'Влияние произведения': ").strip()

    final_score = calculate_final_score(idea, style, plot, emotion, influence, weights)
    print(f"Конечная оценка: {final_score:.2f}/100")
    save_to_db = input("Сохранить отзыв в базу данных? (y/n): ").strip().lower()
    review_id = None
    if save_to_db == "y":
        review = Review(title=title, author=author, evaluator=username, genre=genre,
                        idea=idea, style=style, plot=plot, emotion=emotion, influence=influence,
                        final_score=final_score, review_date=datetime.date.today(),
                        idea_reason=idea_reason, style_reason=style_reason,
                        plot_reason=plot_reason, emotion_reason=emotion_reason,
                        influence_reason=influence_reason)
        session.add(review)
        session.commit()
        review_id = review.id
        print("✅ Отзыв сохранён в базе данных.")
    else:
        print("❌ Отзыв не сохранён в базе данных.")
    session.close()
    
    save_file = input("Сохранить подробное описание оценки в файл? (y/n): ").strip().lower()
    if save_file == "y":
        save_review_to_file(title, author, username, genre, idea, idea_reason,
                            style, style_reason, plot, plot_reason,
                            emotion, emotion_reason, influence,
                            influence_reason, final_score)
        plot_review_scores(idea, style, plot, emotion, influence)
    
    # Если отзыв сохранён, проверяем, есть ли расхождение с жанровым средним
    if review_id is not None:
        adaptive_review_check(genre, final_score, review_id)

def view_reviews():
    session = Session()
    reviews = session.query(Review).all()
    if not reviews:
        print("❌ Нет сохранённых оценок.")
    else:
        for review in reviews:
            print(f"\nID: {review.id}")
            print(f"📖 {review.title} ({review.author}) - {review.genre}")
            print(f"Оценка: {review.final_score}/100")
            print(f"Оценил: {review.evaluator} | Дата: {review.review_date}")
    session.close()

def delete_review():
    session = Session()
    review_id = input("Введите ID оценки для удаления: ").strip()
    review = session.query(Review).filter_by(id=review_id).first()
    if not review:
        print("❌ Оценка не найдена.")
    else:
        session.delete(review)
        session.commit()
        print("✅ Оценка успешно удалена.")
    session.close()

def simulate_loading():
    print("Загрузка, подождите...")
    total = 20
    for i in range(total):
        sys.stdout.write("\r[" + "#"*(i+1) + " "*(total-i-1) + "]")
        sys.stdout.flush()
        time.sleep(0.1)
    print("\n")

def main():
    print("\n🔹 Добро пожаловать в систему оценки книг 🔹")
    simulate_loading()  # Показываем анимацию загрузки после приветствия
    create_tables()
    logged_in = False
    current_user = None
    while True:
        if not logged_in:
            print("1. Войти в систему")
            print("2. Зарегистрировать нового редактора")
            print("3. Выйти")
            choice = input("Выберите действие: ").strip()
            if choice == "1":
                username = input("Введите логин: ").strip()
                password = input("Введите пароль: ").strip()
                if login_editor(username, password):
                    logged_in = True
                    current_user = username
                    print("✅ Успешный вход.")
                else:
                    print("❌ Ошибка входа. Проверьте логин и пароль.")
            elif choice == "2":
                register_editor()
            elif choice == "3":
                print("👋 До свидания!")
                break
            else:
                print("❌ Некорректный ввод. Попробуйте снова.")
        else:
            print("1. Просмотреть все оценки")
            print("2. Редактировать оценку")
            print("3. Написать отзыв")
            print("4. Удалить оценку")
            print("5. Выйти из системы")
            choice = input("Выберите действие: ").strip()
            if choice == "1":
                view_reviews()
            elif choice == "2":
                edit_review()
            elif choice == "3":
                write_review(current_user)
            elif choice == "4":
                delete_review()
            elif choice == "5":
                logged_in = False
                current_user = None
                print("✅ Вы вышли из системы.")
            else:
                print("❌ Некорректный ввод. Попробуйте снова.")
                
if __name__ == "__main__":
    main()
