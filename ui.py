# Стандартные библиотеки
from tkinter import *
from tkinter import ttk, simpledialog, messagebox, filedialog
import datetime
import threading

# Внешние зависимости
import bcrypt

# Локальные модули
from database import (
    create_tables, login_editor, Session, 
    Review, Editor, DeletedReview
)
from analytics import ReviewAnalytics, calculate_final_score  # Исправленный импорт
from genres import genre_weights

# Константы
WINDOW_SIZE = "800x600"
PADDING = 10
BUTTON_WIDTH = 25

class BookReviewUI:
    def __init__(self):
        self.root = None
        self.main_frame = None
        self.current_user = None
        self.style = None
        self.setup_ui()

    def setup_ui(self):
        # Создаем главное окно до показа splash screen
        self.root = Tk()
        self.root.withdraw()  # Скрываем главное окно до завершения загрузки
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Показываем splash screen
        splash = self.show_loading_screen()
        
        # Настраиваем главное окно
        self.root.title("Система оценки книг")
        self.root.geometry(WINDOW_SIZE)
        
        self.setup_styles()
        self.init_database()
        
        # После загрузки показываем главное окно
        self.root.deiconify()

    def show_loading_screen(self):
        """Улучшенный экран загрузки"""
        splash = Toplevel()
        splash.title("Загрузка")
        
        # Размещаем окно по центру экрана
        w = 300
        h = 150
        ws = splash.winfo_screenwidth()
        hs = splash.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        splash.geometry(f'{w}x{h}+{int(x)}+{int(y)}')
        
        splash.overrideredirect(True)
        splash.attributes('-topmost', True)
        
        # Создаем и размещаем виджеты
        ttk.Label(
            splash,
            text="Загрузка системы...",
            font=("Arial", 12)
        ).pack(pady=20)
        
        progress = ttk.Progressbar(
            splash,
            mode='determinate',
            length=200
        )
        progress.pack(pady=10)
        
        status_label = ttk.Label(
            splash,
            text="Инициализация..."
        )
        status_label.pack(pady=5)
        
        splash.update()
        
        return splash, progress, status_label

    def init_database(self):
        """Инициализация с отображением прогресса"""
        splash, progress, status = self.show_loading_screen()
        
        def update_status(msg, value):
            status.config(text=msg)
            progress['value'] = value
            splash.update()
        
        try:
            # Пошаговая инициализация с обновлением прогресса
            update_status("Подключение к базе данных...", 20)
            self.root.after(500)  # Имитация загрузки
            
            update_status("Создание таблиц...", 40)
            create_tables()
            self.root.after(500)
            
            update_status("Настройка интерфейса...", 60)
            self.main_frame = ttk.Frame(self.root, padding=PADDING)
            self.main_frame.pack(fill=BOTH, expand=True)
            self.root.after(500)
            
            update_status("Завершение...", 100)
            self.root.after(500)
            
        finally:
            splash.destroy()
            self.show_login_ui()

    def on_close(self):
        """Обработчик закрытия окна"""
        if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
            self.root.quit()
            self.root.destroy()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Современные стили
        self.style.configure(
            'TButton',
            padding=6,
            relief="flat",
            background="#2196f3",
            font=('Arial', 10)
        )
        self.style.configure(
            'TFrame',
            background="#f5f5f5"
        )
        self.style.configure(
            'Header.TLabel',
            font=('Arial', 14, 'bold'),
            background="#f5f5f5",
            padding=10
        )

    def show_login_ui(self):
        """Улучшенное окно входа"""
        self.clear_frame()
        
        ttk.Label(
            self.main_frame,
            text="Добро пожаловать!",
            style='Header.TLabel'
        ).pack(pady=10)
        
        # Форма входа
        login_frame = ttk.LabelFrame(self.main_frame, text="Вход в систему", padding=20)
        login_frame.pack(padx=20, pady=20)
        
        # Username
        ttk.Label(login_frame, text="Логин:").grid(row=0, column=0, pady=5, sticky='e')
        username_var = StringVar()
        username_entry = ttk.Entry(login_frame, textvariable=username_var, width=30)
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        ttk.Label(login_frame, text="Пароль:").grid(row=1, column=0, pady=5, sticky='e')
        password_var = StringVar()
        password_entry = ttk.Entry(
            login_frame,
            textvariable=password_var,
            show="*",
            width=30
        )
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        def try_login():
            username = username_var.get().strip()
            password = password_var.get().strip()
            
            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
                
            if login_editor(username, password):
                self.current_user = username
                self.show_main_menu()
            else:
                messagebox.showerror("Ошибка", "Неверные учетные данные")
                password_var.set("")
        
        ttk.Button(
            button_frame,
            text="Войти",
            command=try_login,
            width=15
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Регистрация",
            command=self.show_register_ui,
            width=15
        ).pack(side=LEFT, padx=5)
        
        # Bind Enter key
        username_entry.bind('<Return>', lambda e: password_entry.focus())
        password_entry.bind('<Return>', lambda e: try_login())
        
        # Set initial focus
        username_entry.focus()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_frame()
        
        ttk.Label(
            self.main_frame,
            text=f"Главное меню | Пользователь: {self.current_user}",
            style='Header.TLabel'
        ).pack()
        
        # Создаем фрейм для кнопок с прокруткой
        canvas = Canvas(self.main_frame)
        scrollbar = ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=canvas.yview)
        buttons_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Добавляем кнопки меню
        menu_buttons = [
            ("Написать отзыв", self.show_write_review_ui),
            ("Просмотреть отзывы", self.show_reviews_list),
            ("Поиск отзывов", self.show_search_ui),
            ("Статистика", self.show_statistics_ui),
            ("Настройки", self.show_settings_ui),
            ("Выход", self.logout)
        ]
        
        for text, command in menu_buttons:
            ttk.Button(
                buttons_frame,
                text=text,
                command=command,
                width=BUTTON_WIDTH
            ).pack(pady=3)
        
        # Настраиваем прокрутку
        canvas.create_window((0, 0), window=buttons_frame, anchor=NW)
        buttons_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=RIGHT, fill=Y)

    def show_write_review_ui(self):
        """Окно создания нового отзыва"""
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Новый отзыв", style='Header.TLabel').pack()
        
        # Создаем фрейм для полей ввода
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(pady=10, padx=10, fill=X)
        
        # Базовая информация
        fields = {
            'title': ('Название книги', ''),
            'author': ('Автор', ''),
            'genre': ('Жанр', '')
        }
        
        entries = {}
        for key, (label, default) in fields.items():
            frame = ttk.Frame(input_frame)
            frame.pack(fill=X, pady=5)
            ttk.Label(frame, text=label).pack(side=LEFT)
            entry = ttk.Entry(frame)
            entry.pack(side=RIGHT, expand=True, fill=X, padx=10)
            entry.insert(0, default)
            entries[key] = entry
            
        # Оценки
        scores_frame = ttk.LabelFrame(self.main_frame, text="Оценки (0-20)")
        scores_frame.pack(pady=10, padx=10, fill=X)
        
        score_entries = {}
        for field in ['idea', 'style', 'plot', 'emotion', 'influence']:
            frame = ttk.Frame(scores_frame)
            frame.pack(fill=X, pady=5)
            ttk.Label(frame, text=field.capitalize()).pack(side=LEFT)
            entry = ttk.Entry(frame, width=10)
            entry.pack(side=RIGHT, padx=10)
            score_entries[field] = entry
            
            # Поле для причины
            reason_entry = ttk.Entry(frame)
            reason_entry.pack(side=RIGHT, expand=True, fill=X, padx=10)
            reason_entry.insert(0, f"Причина для {field}")
            score_entries[f"{field}_reason"] = reason_entry

        def save_review():
            # Валидация данных
            try:
                scores = {k: int(score_entries[k].get()) for k in ['idea', 'style', 'plot', 'emotion', 'influence']}
                for score in scores.values():
                    if not 0 <= score <= 20:
                        raise ValueError("Оценки должны быть от 0 до 20")
                        
                reasons = {f"{k}_reason": score_entries[f"{k}_reason"].get() 
                         for k in ['idea', 'style', 'plot', 'emotion', 'influence']}
                
                title = entries['title'].get().strip()
                author = entries['author'].get().strip()
                genre = entries['genre'].get().strip().lower()
                
                if not all([title, author, genre]):
                    raise ValueError("Заполните все поля")
                
                # Получение весов для жанра
                weights = genre_weights.get(genre)
                if not weights:
                    weights = self.get_custom_weights()
                    if not weights:
                        return
                
                # Расчет итоговой оценки
                final_score = calculate_final_score(
                    scores['idea'], scores['style'], scores['plot'],
                    scores['emotion'], scores['influence'], weights
                )
                
                # Сохранение в БД
                session = Session()
                review = Review(
                    title=title, author=author,
                    evaluator=self.current_user,
                    genre=genre,
                    **scores,
                    **reasons,
                    final_score=final_score,
                    review_date=datetime.date.today()
                )
                session.add(review)
                session.commit()
                session.close()
                
                messagebox.showinfo("Успех", f"Отзыв сохранен. Итоговая оценка: {final_score:.2f}/100")
                self.show_main_menu()
                
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Неизвестная ошибка: {e}")

        # Кнопки действий
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Сохранить", command=save_review).pack(side=LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", command=self.show_main_menu).pack(side=LEFT, padx=5)

    def get_custom_weights(self):
        """Получение пользовательских весов для безжанровой книги"""
        weights_window = Toplevel(self.root)
        weights_window.title("Указание весов")
        weights_window.geometry("300x250")
        
        entries = {}
        for field in ['idea', 'style', 'plot', 'emotion', 'influence']:
            frame = ttk.Frame(weights_window)
            frame.pack(fill=X, pady=5, padx=10)
            ttk.Label(frame, text=f"Вес для {field}:").pack(side=LEFT)
            entry = ttk.Entry(frame, width=10)
            entry.pack(side=RIGHT)
            entries[field] = entry
            
        result = {}
        
        def save_weights():
            try:
                weights = {k: float(entries[k].get()) for k in entries}
                if abs(sum(weights.values()) - 1.0) > 0.01:
                    raise ValueError("Сумма весов должна быть равна 1")
                result.update(weights)
                weights_window.destroy()
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
                
        ttk.Button(weights_window, text="Сохранить", command=save_weights).pack(pady=10)
        
        weights_window.wait_window()
        return result if result else None

    def show_change_password_ui(self):
        self.clear_frame()
        ttk.Label(self.main_frame, text="Смена пароля", style='Header.TLabel').pack()
        
        frame = ttk.Frame(self.main_frame)
        frame.pack(pady=20)
        
        current_pwd = ttk.Entry(frame, show="*")
        current_pwd.insert(0, "Текущий пароль")
        current_pwd.pack(pady=5)
        
        new_pwd = ttk.Entry(frame, show="*")
        new_pwd.insert(0, "Новый пароль")
        new_pwd.pack(pady=5)
        
        def change_pwd():
            current = current_pwd.get().strip()
            new = new_pwd.get().strip()
            
            session = Session()
            editor = session.query(Editor).filter_by(username=self.current_user).first()
            
            if bcrypt.checkpw(current.encode(), editor.password_hash.encode()):
                editor.password_hash = bcrypt.hashpw(new.encode(), bcrypt.gensalt()).decode()
                session.commit()
                messagebox.showinfo("Успех", "Пароль изменен")
                self.show_main_menu()
            else:
                messagebox.showerror("Ошибка", "Неверный текущий пароль")
            session.close()
        
        ttk.Button(frame, text="Изменить пароль", command=change_pwd).pack(pady=5)
        ttk.Button(frame, text="Назад", command=self.show_main_menu).pack(pady=5)

    def show_delete_review_ui(self):
        self.clear_frame()
        ttk.Label(self.main_frame, text="Удаление отзыва", style='Header.TLabel').pack()
        
        session = Session()
        reviews = session.query(Review).all()
        
        if not reviews:
            ttk.Label(self.main_frame, text="Нет отзывов для удаления").pack(pady=20)
            session.close()
            ttk.Button(self.main_frame, text="Назад", command=self.show_main_menu).pack()
            return
            
        for review in reviews:
            frame = ttk.Frame(self.main_frame)
            frame.pack(fill=X, pady=5, padx=10)
            
            ttk.Label(frame, text=f"{review.title} ({review.final_score}/100)").pack(side=LEFT)
            
            def make_delete_command(rev_id):
                return lambda: self.delete_review(rev_id)
                
            ttk.Button(frame, text="Удалить", 
                      command=make_delete_command(review.id)).pack(side=RIGHT)
                      
        session.close()
        ttk.Button(self.main_frame, text="Назад", command=self.show_main_menu).pack(pady=20)

    def delete_review(self, review_id):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот отзыв?"):
            reasons = ["Не соответствует правилам", "Нет причины критерий", "Оценка не точна", "Другое"]
            reason = simpledialog.askstring(
                "Причина удаления",
                "Укажите причину удаления:",
                initialvalue=reasons[0]
            )
            if reason:
                session = Session()
                review = session.query(Review).filter_by(id=review_id).first()
                if review:
                    session.delete(review)
                    session.commit()
                    
                    # Сохраняем информацию об удалении
                    del_review = DeletedReview(
                        review_id=review_id,
                        deletion_reason=reasons.index(reason) + 1 if reason in reasons else 0
                    )
                    session.add(del_review)
                    session.commit()
                    
                session.close()
                self.show_delete_review_ui()  # Обновляем список

    def show_reviews_list(self):
        """Показ списка отзывов в основном фрейме"""
        self.clear_frame()
        
        # Заголовок и управление
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=5)
        
        ttk.Label(
            header_frame,
            text="Список отзывов",
            style='Header.TLabel'
        ).pack(side=LEFT)
        
        # Кнопка сравнения
        ttk.Button(
            header_frame,
            text="Сравнить выбранные",
            command=self.compare_selected_reviews
        ).pack(side=RIGHT, padx=5)
        
        # Фрейм поиска и списка
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=BOTH, expand=True)
        
        # Поиск
        search_frame = ttk.Frame(content_frame)
        search_frame.pack(fill=X, pady=5)
        
        search_var = StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=LEFT, fill=X, expand=True)
        
        def filter_reviews():
            query = search_var.get().strip()
            self.update_reviews_list(query)
            
        ttk.Button(
            search_frame,
            text="Поиск",
            command=filter_reviews
        ).pack(side=RIGHT, padx=5)
        
        # Список отзывов с чекбоксами
        self.selected_reviews = []  # Для хранения выбранных отзывов
        self.update_reviews_list("")
        
        # Нижняя панель с кнопками
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=X, pady=5)
        
        ttk.Button(
            button_frame,
            text="Назад в меню",
            command=self.show_main_menu
        ).pack(side=RIGHT)

    def compare_selected_reviews(self):
        """Сравнение выбранных отзывов"""
        if len(self.selected_reviews) < 2:
            messagebox.showwarning(
                "Предупреждение",
                "Выберите минимум 2 книги для сравнения"
            )
            return
        
        if len(self.selected_reviews) > 5:
            messagebox.showwarning(
                "Предупреждение",
                "Можно сравнивать максимум 5 книг"
            )
            return
            
        # Создаем окно сравнения
        comparison_window = Toplevel(self.root)
        comparison_window.title("Сравнение книг")
        comparison_window.geometry("800x600")
        
        # Показываем графики
        fig = ReviewAnalytics.compare_reviews(self.selected_reviews)
        
        # Показываем текстовый отчет
        text_report = ReviewAnalytics.get_comparison_report(self.selected_reviews)
        text_area = Text(comparison_window, wrap=WORD)
        text_area.pack(fill=BOTH, expand=True, padx=10, pady=10)
        text_area.insert(END, text_report)
        
        def save_comparison():
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")]
            )
            if filename:
                ReviewAnalytics.compare_reviews(
                    self.selected_reviews,
                    save_path=filename
                )
                
        ttk.Button(
            comparison_window,
            text="Сохранить график",
            command=save_comparison
        ).pack(pady=5)

    def update_reviews_list(self, query, container=None):
        """Обновленный метод с поддержкой выбора отзывов"""
        if container is None:
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, ttk.Frame):
                    container = widget
                    break
        
        for widget in container.winfo_children():
            widget.destroy()
            
        session = Session()
        reviews = ReviewAnalytics.search_reviews(query)
        
        if not reviews:
            ttk.Label(container, text="Отзывы не найдены").pack(pady=10)
        else:
            for review in reviews:
                review_frame = ttk.Frame(container)
                review_frame.pack(fill=X, pady=2)
                
                var = BooleanVar()
                check = ttk.Checkbutton(
                    review_frame,
                    variable=var,
                    command=lambda r=review, v=var: self.on_review_select(r, v)
                )
                check.pack(side=LEFT)
                
                # Основная информация
                info_frame = ttk.Frame(review_frame)
                info_frame.pack(fill=X)
                
                ttk.Label(
                    info_frame,
                    text=f"📖 {review.title}",
                    font=('Arial', 10, 'bold')
                ).pack(side=LEFT)
                
                ttk.Label(
                    info_frame,
                    text=f"Оценка: {review.final_score:.1f}/100"
                ).pack(side=RIGHT)
                
                # Кнопки действий
                buttons_frame = ttk.Frame(review_frame)
                buttons_frame.pack(fill=X, pady=2)
                
                def make_edit_command(rev):
                    return lambda: self.edit_review_inline(rev, review_frame)
                    
                def make_delete_command(rev_id):
                    return lambda: self.delete_review_with_confirm(rev_id)
                
                ttk.Button(
                    buttons_frame,
                    text="Редактировать",
                    command=make_edit_command(review)
                ).pack(side=LEFT, padx=2)
                
                ttk.Button(
                    buttons_frame,
                    text="Удалить",
                    command=make_delete_command(review.id)
                ).pack(side=LEFT, padx=2)
                
                ttk.Separator(review_frame, orient=HORIZONTAL).pack(fill=X, pady=5)
                
        session.close()

    def on_review_select(self, review, var):
        """Обработка выбора отзыва для сравнения"""
        if var.get():
            if review not in self.selected_reviews:
                self.selected_reviews.append(review)
        else:
            if review in self.selected_reviews:
                self.selected_reviews.remove(review)

    def edit_review_inline(self, review, container):
        """Редактирование отзыва прямо в списке"""
        for widget in container.winfo_children():
            widget.destroy()
            
        # Поля для редактирования
        fields_frame = ttk.Frame(container)
        fields_frame.pack(fill=X, pady=5)
        
        entries = {}
        for field in ['idea', 'style', 'plot', 'emotion', 'influence']:
            frame = ttk.Frame(fields_frame)
            frame.pack(fill=X, pady=2)
            
            ttk.Label(frame, text=field.capitalize()).pack(side=LEFT)
            entry = ttk.Entry(frame, width=10)
            entry.insert(0, str(getattr(review, field)))
            entry.pack(side=RIGHT)
            entries[field] = entry
            
            reason_entry = ttk.Entry(frame)
            reason_entry.insert(0, getattr(review, f"{field}_reason"))
            reason_entry.pack(side=RIGHT, fill=X, expand=True, padx=5)
            entries[f"{field}_reason"] = reason_entry
            
        def save_changes():
            try:
                # Валидация и сохранение изменений
                scores = {k: int(entries[k].get()) for k in ['idea', 'style', 'plot', 'emotion', 'influence']}
                reasons = {f"{k}_reason": entries[f"{k}_reason"].get() 
                         for k in ['idea', 'style', 'plot', 'emotion', 'influence']}
                
                
                for score in scores.values():
                    if not 0 <= score <= 20:
                        raise ValueError("Оценки должны быть от 0 до 20")
                
                # Получаем веса для расчета
                weights = genre_weights.get(review.genre)
                if not weights:
                    weights = self.get_custom_weights()
                    if not weights:
                        return
                
                final_score = calculate_final_score(
                    scores['idea'], scores['style'],
                    scores['plot'], scores['emotion'],
                    scores['influence'], weights
                )
                
                session = Session()
                db_review = session.query(Review).get(review.id)
                
                for k, v in scores.items():
                    setattr(db_review, k, v)
                for k, v in reasons.items():
                    setattr(db_review, k, v)
                    
                db_review.final_score = final_score
                db_review.review_date = datetime.date.today()
                
                session.commit()
                session.close()
                
                self.update_reviews_list("")  # Обновляем список
                
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
                
        # Кнопки действий
        ttk.Button(
            container,
            text="Сохранить",
            command=save_changes
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            container,
            text="Отмена",
            command=lambda: self.update_reviews_list("")
        ).pack(side=LEFT)

    def logout(self):
        """Выход из системы"""
        if messagebox.askyesno("Подтверждение", "Вы действительно хотите выйти?"):
            self.current_user = None
            self.show_login_ui()

    def show_register_ui(self):
        """Окно регистрации нового пользователя"""
        register_window = Toplevel(self.root)
        register_window.title("Регистрация")
        register_window.geometry("300x200")
        register_window.transient(self.root)
        register_window.grab_set()
        
        frame = ttk.LabelFrame(register_window, text="Регистрация нового пользователя", padding=20)
        frame.pack(padx=20, pady=20, fill=BOTH, expand=True)
        
        # Username
        ttk.Label(frame, text="Логин:").pack(fill=X)
        username_var = StringVar()
        username_entry = ttk.Entry(frame, textvariable=username_var)
        username_entry.pack(fill=X, pady=(0, 10))
        
        # Password
        ttk.Label(frame, text="Пароль:").pack(fill=X)
        password_var = StringVar()
        password_entry = ttk.Entry(frame, textvariable=password_var, show="*")
        password_entry.pack(fill=X, pady=(0, 10))
        
        def try_register():
            username = username_var.get().strip()
            password = password_var.get().strip()
            
            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
                
            session = Session()
            existing = session.query(Editor).filter_by(username=username).first()
            
            if existing:
                messagebox.showerror("Ошибка", "Такой пользователь уже существует!")
                session.close()
                return
                
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            new_editor = Editor(username=username, password_hash=password_hash)
            
            try:
                session.add(new_editor)
                session.commit()
                messagebox.showinfo("Успех", "Регистрация успешна!")
                register_window.destroy()
            except Exception as e:
                session.rollback()
                messagebox.showerror("Ошибка", f"Ошибка регистрации: {e}")
            finally:
                session.close()
        
        # Кнопки
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Зарегистрироваться",
            command=try_register
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Отмена",
            command=register_window.destroy
        ).pack(side=LEFT)
        
        # Фокус и бинды
        username_entry.focus()
        username_entry.bind('<Return>', lambda e: password_entry.focus())
        password_entry.bind('<Return>', lambda e: try_register())

def main():
    app = BookReviewUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
