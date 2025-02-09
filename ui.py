from tkinter import *
from tkinter import simpledialog, messagebox
import datetime
from database import create_tables, login_editor, register_editor, Session, Review
from formula import calculate_final_score
from main import genre_weights, save_review_to_file, plot_review_scores

current_user = None
root = None
auth_frame = None
app_frame = None

def login():
    global current_user
    username = simpledialog.askstring("Вход", "Введите логин:")
    password = simpledialog.askstring("Вход", "Введите пароль:", show='*')
    if username and password:
        if login_editor(username, password):
            current_user = username
            messagebox.showinfo("Успех", "Успешный вход!")
            show_app_ui()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")

def register():
    username = simpledialog.askstring("Регистрация", "Введите новый логин:")
    password = simpledialog.askstring("Регистрация", "Введите новый пароль:", show='*')
    if username and password:
        session = Session()
        try:
            register_editor()
            messagebox.showinfo("Регистрация", "Редактор зарегистрирован.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка регистрации: {e}")
        finally:
            session.close()

def view_reviews_ui():
    session = Session()
    reviews = session.query(Review).all()
    session.close()
    win = Toplevel(root)
    win.title("Просмотр отзывов")
    text_area = Text(win, width=80, height=20)
    text_area.pack(padx=10, pady=10)
    if not reviews:
        text_area.insert(END, "❌ Нет сохранённых оценок.")
    else:
        for review in reviews:
            text_area.insert(END, f"ID: {review.id}\n")
            text_area.insert(END, f"📖 {review.title} ({review.author}) - {review.genre}\n")
            text_area.insert(END, f"Оценка: {review.final_score}/100\n")
            text_area.insert(END, f"Оценил: {review.evaluator} | Дата: {review.review_date}\n")
            text_area.insert(END, f"Причина 'Идея': {review.idea_reason}\n")
            text_area.insert(END, f"Причина 'Стиль': {review.style_reason}\n")
            text_area.insert(END, f"Причина 'Сюжет': {review.plot_reason}\n")
            text_area.insert(END, f"Причина 'Эмоции': {review.emotion_reason}\n")
            text_area.insert(END, f"Причина 'Влияние': {review.influence_reason}\n")
            text_area.insert(END, "-------------------------\n")

def write_review_ui():
    global current_user
    if not current_user:
        messagebox.showerror("Ошибка", "Сначала войдите в систему!")
        return
    title = simpledialog.askstring("Новый отзыв", "Название книги:")
    author = simpledialog.askstring("Новый отзыв", "Автор:")
    genre_str = simpledialog.askstring("Новый отзыв", "Жанр:")
    if not all([title, author, genre_str]):
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
        return
    genre = genre_str.lower()
    try:
        idea = int(simpledialog.askstring("Новый отзыв", "Оценка 'Идея' (0-20):"))
        style = int(simpledialog.askstring("Новый отзыв", "Оценка 'Стиль' (0-20):"))
        plot = int(simpledialog.askstring("Новый отзыв", "Оценка 'Сюжет' (0-20):"))
        emotion = int(simpledialog.askstring("Новый отзыв", "Оценка 'Эмоции' (0-20):"))
        influence = int(simpledialog.askstring("Новый отзыв", "Оценка 'Влияние' (0-20):"))
    except Exception:
        messagebox.showerror("Ошибка", "Некорректный ввод числовых значений.")
        return
    idea_reason = simpledialog.askstring("Причина оценки", "Причина 'Идея':", initialvalue="", parent=root)
    style_reason = simpledialog.askstring("Причина оценки", "Причина 'Стиль':", initialvalue="", parent=root)
    plot_reason = simpledialog.askstring("Причина оценки", "Причина 'Сюжет':", initialvalue="", parent=root)
    emotion_reason = simpledialog.askstring("Причина оценки", "Причина 'Эмоции':", initialvalue="", parent=root)
    influence_reason = simpledialog.askstring("Причина оценки", "Причина 'Влияние':", initialvalue="", parent=root)
    weights = genre_weights.get(genre)
    if weights is None or genre == "безжанровый":
        messagebox.showinfo("Информация", "Безжанровый режим активирован. Укажите веса вручную.")
        try:
            idea_w = float(simpledialog.askstring("Вес", "Вес для 'Идея':"))
            style_w = float(simpledialog.askstring("Вес", "Вес для 'Стиль':"))
            plot_w = float(simpledialog.askstring("Вес", "Вес для 'Сюжет':"))
            emotion_w = float(simpledialog.askstring("Вес", "Вес для 'Эмоции':"))
            influence_w = float(simpledialog.askstring("Вес", "Вес для 'Влияние' (бонус):"))
            weights = {"idea": idea_w, "style": style_w, "plot": plot_w, "emotion": emotion_w, "influence": influence_w}
        except Exception:
            messagebox.showerror("Ошибка", "Некорректный ввод весов.")
            return
    final_score = calculate_final_score(idea, style, plot, emotion, influence, weights)
    messagebox.showinfo("Итоговая оценка", f"Конечная оценка: {final_score:.2f}/100")
    session = Session()
    review = Review(title=title, author=author, evaluator=current_user, genre=genre,
                    idea=idea, style=style, plot=plot, emotion=emotion, influence=influence,
                    final_score=final_score, review_date=datetime.date.today(),
                    idea_reason=idea_reason, style_reason=style_reason,
                    plot_reason=plot_reason, emotion_reason=emotion_reason,
                    influence_reason=influence_reason)
    session.add(review)
    session.commit()
    session.close()
    messagebox.showinfo("Отзыв", "Отзыв сохранён в базе данных.")
    
    save_file = messagebox.askyesno("Сохранить в файл", "Сохранить подробное описание оценки в файл?")
    if save_file:
        save_review_to_file(title, author, current_user, genre, idea, idea_reason,
                            style, style_reason, plot, plot_reason,
                            emotion, emotion_reason, influence, influence_reason, final_score)
    
    plot_graph = messagebox.askyesno("Показать график", "Показать график оценок?")
    if plot_graph:
        plot_review_scores(idea, style, plot, emotion, influence)

def edit_review_ui():
    review_id = simpledialog.askstring("Редактировать отзыв", "Введите ID отзыва для редактирования:")
    if not review_id:
        messagebox.showerror("Ошибка", "ID отзыва не введён!")
        return
    session = Session()
    review = session.query(Review).filter_by(id=review_id).first()
    if not review:
        messagebox.showerror("Ошибка", "Отзыв не найден!")
        session.close()
        return
    new_idea = simpledialog.askinteger("Редактировать отзыв", f"Новая оценка 'Идея' (текущее {review.idea}):")
    new_style = simpledialog.askinteger("Редактировать отзыв", f"Новая оценка 'Стиль' (текущее {review.style}):")
    new_plot = simpledialog.askinteger("Редактировать отзыв", f"Новая оценка 'Сюжет' (текущее {review.plot}):")
    new_emotion = simpledialog.askinteger("Редактировать отзыв", f"Новая оценка 'Эмоции' (текущее {review.emotion}):")
    new_influence = simpledialog.askinteger("Редактировать отзыв", f"Новая оценка 'Влияние' (текущее {review.influence}):")
    
    new_idea_reason = simpledialog.askstring("Редактировать отзыв", "Новая причина 'Идея':", initialvalue=review.idea_reason, parent=root)
    new_style_reason = simpledialog.askstring("Редактировать отзыв", "Новая причина 'Стиль':", initialvalue=review.style_reason, parent=root)
    new_plot_reason = simpledialog.askstring("Редактировать отзыв", "Новая причина 'Сюжет':", initialvalue=review.plot_reason, parent=root)
    new_emotion_reason = simpledialog.askstring("Редактировать отзыв", "Новая причина 'Эмоции':", initialvalue=review.emotion_reason, parent=root)
    new_influence_reason = simpledialog.askstring("Редактировать отзыв", "Новая причина 'Влияние':", initialvalue=review.influence_reason, parent=root)
    
    review.idea = new_idea if new_idea is not None else review.idea
    review.style = new_style if new_style is not None else review.style
    review.plot = new_plot if new_plot is not None else review.plot
    review.emotion = new_emotion if new_emotion is not None else review.emotion
    review.influence = new_influence if new_influence is not None else review.influence
    review.idea_reason = new_idea_reason or review.idea_reason
    review.style_reason = new_style_reason or review.style_reason
    review.plot_reason = new_plot_reason or review.plot_reason
    review.emotion_reason = new_emotion_reason or review.emotion_reason
    review.influence_reason = new_influence_reason or review.influence_reason
    
    weights = genre_weights.get(review.genre)
    if weights is None or review.genre == "безжанровый":
        messagebox.showinfo("Информация", "Безжанровый режим: укажите веса вручную.")
        try:
            idea_w = float(simpledialog.askstring("Вес", "Вес для 'Идея':"))
            style_w = float(simpledialog.askstring("Вес", "Вес для 'Стиль':"))
            plot_w = float(simpledialog.askstring("Вес", "Вес для 'Сюжет':"))
            emotion_w = float(simpledialog.askstring("Вес", "Вес для 'Эмоции':"))
            influence_w = float(simpledialog.askstring("Вес", "Вес для 'Влияние':"))
            weights = {"idea": idea_w, "style": style_w, "plot": plot_w, "emotion": emotion_w, "influence": influence_w}
        except Exception:
            messagebox.showerror("Ошибка", "Неверный ввод весов. Отмена редактирования.")
            session.close()
            return
    review.final_score = calculate_final_score(review.idea, review.style, review.plot,
                                                review.emotion, review.influence, weights)
    session.commit()
    session.close()
    messagebox.showinfo("Успех", "Отзыв успешно обновлён!")

def delete_review_ui():
    review_id = simpledialog.askstring("Удалить отзыв", "Введите ID отзыва для удаления:")
    if not review_id:
        messagebox.showerror("Ошибка", "ID отзыва не введён!")
        return
    session = Session()
    review = session.query(Review).filter_by(id=review_id).first()
    if not review:
        messagebox.showerror("Ошибка", "Отзыв не найден!")
        session.close()
        return
    confirm = messagebox.askyesno("Подтвердить удаление", f"Удалить отзыв '{review.title}'?")
    if confirm:
        session.delete(review)
        session.commit()
        messagebox.showinfo("Успех", "Отзыв удалён.")
    session.close()

def show_auth_ui():
    global auth_frame, app_frame
    if app_frame is not None:
        app_frame.pack_forget()
    auth_frame.pack(fill=BOTH, expand=True)

def show_app_ui():
    global auth_frame, app_frame
    if auth_frame is not None:
        auth_frame.pack_forget()
    app_frame.pack(fill=BOTH, expand=True)

def create_ui():
    global root, auth_frame, app_frame
    create_tables()
    root = Tk()
    root.title("Система оценки книг")
    root.geometry("400x400")
    
    auth_frame = Frame(root)
    Button(auth_frame, text="Войти", width=25, command=login).pack(pady=5)
    Button(auth_frame, text="Регистрация", width=25, command=register).pack(pady=5)
    auth_frame.pack(fill=BOTH, expand=True)
    
    app_frame = Frame(root)
    Button(app_frame, text="Просмотреть отзывы", width=25, command=view_reviews_ui).pack(pady=5)
    Button(app_frame, text="Написать отзыв", width=25, command=write_review_ui).pack(pady=5)
    Button(app_frame, text="Редактировать отзыв", width=25, command=edit_review_ui).pack(pady=5)
    Button(app_frame, text="Удалить отзыв", width=25, command=delete_review_ui).pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    create_ui()
