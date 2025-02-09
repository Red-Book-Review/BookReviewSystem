from tkinter import *
from tkinter import simpledialog, messagebox
import datetime
from database import create_tables, login_editor, register_editor, Session, Review
from formula import calculate_final_score
from genres import genre_weights  # импорт из нового файла жанров
# ...existing imports...

# Можно добавить импорт ttk и сторонних библиотек для tooltips и тем оформления
# from tkinter import ttk
# from ttkthemes import ThemedTk

# Новый класс для всплывающих подсказок
class ToolTip:
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # задержка в мс
        self.wraplength = 180   # ширина текста
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
    def enter(self, event=None):
        self.schedule()
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)
    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)
    def showtip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tw = Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left', background="#ffffe0", relief='solid', borderwidth=1, wraplength=self.wraplength)
        label.pack(ipadx=1)
    def hidetip(self):
        if self.tw:
            self.tw.destroy()
            self.tw = None

current_user = None
root = None
main_frame = None  # Новая основная панель вместо auth_frame/app_frame

def show_loading_screen():
    splash = Toplevel()
    splash.overrideredirect(True)
    splash.geometry("300x100+500+300")
    Label(splash, text="Загрузка системы...\nПодождите...", font=("Arial", 12)).pack(expand=True)
    splash.update()
    # Уменьшаем задержку (например, 500 мс)
    splash.after(500, splash.destroy)

# Новая функция для показа окна входа в систему
def show_login_ui():
    global main_frame
    for widget in main_frame.winfo_children():
        widget.destroy()
    Label(main_frame, text="Вход в систему", font=("Arial", 14)).pack(pady=10)
    username_entry = Entry(main_frame)
    username_entry.pack(pady=5)
    username_entry.insert(0, "Логин")
    password_entry = Entry(main_frame, show="*")
    password_entry.pack(pady=5)
    password_entry.insert(0, "Пароль")
    
    def perform_login():
        global current_user
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if username and password:
            if login_editor(username, password):
                current_user = username
                messagebox.showinfo("Успех", "Успешный вход!")
                show_menu_ui()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль.")
        else:
            messagebox.showerror("Ошибка", "Заполните оба поля!")
    
    btn_login = Button(main_frame, text="Войти", width=25, command=perform_login)
    btn_login.pack(pady=5)
    btn_register = Button(main_frame, text="Регистрация", width=25, command=register)
    btn_register.pack(pady=5)
    # ...можно добавить кнопку выхода...
    
# Новая функция – основное меню для всех действий
def show_menu_ui():
    for widget in main_frame.winfo_children():
        widget.destroy()
    Label(main_frame, text=f"Меню (Пользователь: {current_user})", font=("Arial", 14)).pack(pady=10)
    
    # Кнопки запускают функции, которые (при необходимости) обновляют main_frame
    Button(main_frame, text="Написать отзыв", width=25, command=write_review_ui).pack(pady=3)
    Button(main_frame, text="Редактировать отзыв", width=25, command=edit_review_ui).pack(pady=3)
    Button(main_frame, text="Удалить отзыв", width=25, command=delete_review_ui).pack(pady=3)
    Button(main_frame, text="Просмотреть отзывы", width=25, command=view_reviews_ui).pack(pady=3)
    Button(main_frame, text="Сменить пароль", width=25, command=change_password_ui).pack(pady=3)
    Button(main_frame, text="Выход", width=25, command=root.quit).pack(pady=3)

# Изменяем функции write_review_ui и edit_review_ui для проверки лимитов оценок (0-20)
def write_review_ui():
    if not current_user:
        messagebox.showerror("Ошибка", "Сначала войдите в систему!")
        return
    # Используем simpledialog для ввода остальных данных (можно комбинировать с полями в main_frame)
    title = simpledialog.askstring("Новый отзыв", "Название книги:", parent=main_frame)
    author = simpledialog.askstring("Новый отзыв", "Автор:", parent=main_frame)
    genre_str = simpledialog.askstring("Новый отзыв", "Жанр:", parent=main_frame)
    if not all([title, author, genre_str]):
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
        return
    genre = genre_str.lower()
    try:
        idea = int(simpledialog.askstring("Новый отзыв", "Оценка 'Идея' (0-20):", parent=main_frame))
        style = int(simpledialog.askstring("Новый отзыв", "Оценка 'Стиль' (0-20):", parent=main_frame))
        plot = int(simpledialog.askstring("Новый отзыв", "Оценка 'Сюжет' (0-20):", parent=main_frame))
        emotion = int(simpledialog.askstring("Новый отзыв", "Оценка 'Эмоции' (0-20):", parent=main_frame))
        influence = int(simpledialog.askstring("Новый отзыв", "Оценка 'Влияние' (0-20):", parent=main_frame))
    except Exception:
        messagebox.showerror("Ошибка", "Некорректный ввод числовых значений.")
        return
    # Проверяем лимиты
    for score, crit in [(idea, "Идея"), (style, "Стиль"), (plot, "Сюжет"), (emotion, "Эмоции"), (influence, "Влияние")]:
        if score < 0 or score > 20:
            messagebox.showerror("Ошибка", f"{crit}: балл должен быть от 0 до 20.")
            return
    idea_reason = simpledialog.askstring("Причина оценки", "Причина 'Идея':", initialvalue="", parent=main_frame)
    style_reason = simpledialog.askstring("Причина оценки", "Причина 'Стиль':", initialvalue="", parent=main_frame)
    plot_reason = simpledialog.askstring("Причина оценки", "Причина 'Сюжет':", initialvalue="", parent=main_frame)
    emotion_reason = simpledialog.askstring("Причина оценки", "Причина 'Эмоции':", initialvalue="", parent=main_frame)
    influence_reason = simpledialog.askstring("Причина оценки", "Причина 'Влияние':", initialvalue="", parent=main_frame)
    weights = genre_weights.get(genre)
    if weights is None or genre == "безжанровый":
        messagebox.showinfo("Информация", "Безжанровый режим активирован. Укажите веса вручную.")
        try:
            idea_w = float(simpledialog.askstring("Вес", "Вес для 'Идея':", parent=main_frame))
            style_w = float(simpledialog.askstring("Вес", "Вес для 'Стиль':", parent=main_frame))
            plot_w = float(simpledialog.askstring("Вес", "Вес для 'Сюжет':", parent=main_frame))
            emotion_w = float(simpledialog.askstring("Вес", "Вес для 'Эмоции':", parent=main_frame))
            influence_w = float(simpledialog.askstring("Вес", "Вес для 'Влияние' (бонус):", parent=main_frame))
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

def edit_review_ui():
    review_id = simpledialog.askstring("Редактирование отзыва", "Введите ID отзыва для редактирования:", parent=main_frame)
    if not review_id:
        messagebox.showerror("Ошибка", "ID не указан!")
        return
    session = Session()
    review = session.query(Review).filter_by(id=review_id).first()
    if not review:
        messagebox.showerror("Ошибка", "Отзыв не найден!")
        session.close()
        return
    try:
        new_idea = int(simpledialog.askstring("Редактирование отзыва", "Новая оценка 'Идея' (0-20):", parent=main_frame))
    except (ValueError, TypeError):
        messagebox.showerror("Ошибка", "Некорректное числовое значение для 'Идея'")
        session.close()
        return
    # Проверка лимита для 'Идея'
    if new_idea < 0 or new_idea > 20:
        messagebox.showerror("Ошибка", "'Идея' должна быть от 0 до 20.")
        session.close()
        return
    new_idea_reason = simpledialog.askstring("Редактирование отзыва", "Новая причина 'Идея':", parent=main_frame)
    try:
        new_style = int(simpledialog.askstring("Редактирование отзыва", "Новая оценка 'Стиль' (0-20):", parent=main_frame))
    except (ValueError, TypeError):
        messagebox.showerror("Ошибка", "Некорректное числовое значение для 'Стиль'")
        session.close()
        return
    if new_style < 0 or new_style > 20:
        messagebox.showerror("Ошибка", "'Стиль' должен быть от 0 до 20.")
        session.close()
        return
    new_style_reason = simpledialog.askstring("Редактирование отзыва", "Новая причина 'Стиль':", parent=main_frame)
    try:
        new_plot = int(simpledialog.askstring("Редактирование отзыва", "Новая оценка 'Сюжет' (0-20):", parent=main_frame))
    except (ValueError, TypeError):
        messagebox.showerror("Ошибка", "Некорректное числовое значение для 'Сюжет'")
        session.close()
        return
    if new_plot < 0 or new_plot > 20:
        messagebox.showerror("Ошибка", "'Сюжет' должен быть от 0 до 20.")
        session.close()
        return
    new_plot_reason = simpledialog.askstring("Редактирование отзыва", "Новая причина 'Сюжет':", parent=main_frame)
    try:
        new_emotion = int(simpledialog.askstring("Редактирование отзыва", "Новая оценка 'Эмоции' (0-20):", parent=main_frame))
    except (ValueError, TypeError):
        messagebox.showerror("Ошибка", "Некорректное числовое значение для 'Эмоции'")
        session.close()
        return
    if new_emotion < 0 or new_emotion > 20:
        messagebox.showerror("Ошибка", "'Эмоции' должны быть от 0 до 20.")
        session.close()
        return
    new_emotion_reason = simpledialog.askstring("Редактирование отзыва", "Новая причина 'Эмоции':", parent=main_frame)
    try:
        new_influence = int(simpledialog.askstring("Редактирование отзыва", "Новая оценка 'Влияние' (0-20):", parent=main_frame))
    except (ValueError, TypeError):
        messagebox.showerror("Ошибка", "Некорректное числовое значение для 'Влияние'")
        session.close()
        return
    if new_influence < 0 or new_influence > 20:
        messagebox.showerror("Ошибка", "'Влияние' должно быть от 0 до 20.")
        session.close()
        return
    new_influence_reason = simpledialog.askstring("Редактирование отзыва", "Новая причина 'Влияние':", parent=main_frame)
    weights = genre_weights.get(review.genre)
    if weights is None and review.genre == "безжанровый":
        messagebox.showinfo("Информация", "Безжанровый режим: укажите новые веса вручную.")
        try:
            idea_w = float(simpledialog.askstring("Вес", "Новый вес для 'Идея':", parent=main_frame))
            style_w = float(simpledialog.askstring("Вес", "Новый вес для 'Стиль':", parent=main_frame))
            plot_w = float(simpledialog.askstring("Вес", "Новый вес для 'Сюжет':", parent=main_frame))
            emotion_w = float(simpledialog.askstring("Вес", "Новый вес для 'Эмоции':", parent=main_frame))
            influence_w = float(simpledialog.askstring("Вес", "Новый вес для 'Влияние':", parent=main_frame))
            weights = {"idea": idea_w, "style": style_w, "plot": plot_w, "emotion": emotion_w, "influence": influence_w}
        except Exception:
            messagebox.showerror("Ошибка", "Некорректный ввод весов. Изменения не сохранены.")
            session.close()
            return
    new_final_score = calculate_final_score(new_idea, new_style, new_plot, new_emotion, new_influence, weights)
    review.idea = new_idea
    review.idea_reason = new_idea_reason
    review.style = new_style
    review.style_reason = new_style_reason
    review.plot = new_plot
    review.plot_reason = new_plot_reason
    review.emotion = new_emotion
    review.emotion_reason = new_emotion_reason
    review.influence = new_influence
    review.influence_reason = new_influence_reason
    review.final_score = new_final_score
    review.review_date = datetime.date.today()
    session.commit()
    session.close()
    messagebox.showinfo("Успех", f"Отзыв обновлён, новая оценка: {new_final_score:.2f}/100")

# Для удаления отзыва можно оставить простое окно (без Toplevel), как и просмотр, через main_frame
def delete_review_ui():
    review_id = simpledialog.askstring("Удаление отзыва", "Введите ID отзыва для удаления:", parent=main_frame)
    if not review_id:
        messagebox.showerror("Ошибка", "ID не указан!")
        return
    session = Session()
    review = session.query(Review).filter_by(id=review_id).first()
    if not review:
        messagebox.showerror("Ошибка", "Отзыв не найден!")
        session.close()
        return
    # Вместо создания нового окна – используем simpledialog для выбора причины
    reason = simpledialog.askstring("Причина удаления",
                                    "Введите причину удаления (или стандарт: 'Не соответствует правилам', 'Нет причины критерий', 'Оценка не точна'):", parent=main_frame)
    if reason is None:
        session.close()
        return
    from database import DeletedReview
    mapping = {"Не соответствует правилам": 1,
               "Нет причины критерий": 2,
               "Оценка не точна": 3}
    if reason in mapping:
        del_code = mapping[reason]
        del_session = Session()
        del_record = DeletedReview(review_id=int(review_id), deletion_reason=del_code)
        del_session.add(del_record)
        del_session.commit()
        del_session.close()
    else:
        with open("deletion_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"Отзыв ID {review_id} удалён. Причина: {reason}\n")
    session.delete(review)
    session.commit()
    session.close()
    messagebox.showinfo("Удаление", "Отзыв успешно удалён.")

# Функция смены пароля без изменений
def change_password_ui():
    username = simpledialog.askstring("Смена пароля", "Введите ваш логин:", parent=main_frame)
    if not username:
        messagebox.showerror("Ошибка", "Логин не введён!")
        return
    import database
    database.change_password_editor(username)

# Функция просмотра отзывов – можем вывести их в окно, созданное внутри main_frame
def view_reviews_ui():
    session = Session()
    reviews = session.query(Review).all()
    session.close()
    # Создаём область для просмотра внутри main_frame
    for widget in main_frame.winfo_children():
        widget.destroy()
    Label(main_frame, text="Список отзывов", font=("Arial", 14)).pack(pady=10)
    text_area = Text(main_frame, width=80, height=20)
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
    Button(main_frame, text="Назад в меню", width=25, command=show_menu_ui).pack(pady=5)

def create_ui():
    global root, main_frame
    create_tables()
    root = Tk()
    root.title("Система оценки книг")
    root.geometry("600x500")
    
    show_loading_screen()
    
    main_frame = Frame(root)
    main_frame.pack(fill=BOTH, expand=True)
    # Первый экран – вход в систему
    show_login_ui()
    
    root.mainloop()

if __name__ == "__main__":
    create_ui()
