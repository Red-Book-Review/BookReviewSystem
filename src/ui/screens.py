import tkinter as tk
from tkinter import messagebox
from src.core.auth import AuthManager
from src.core.database.connection import Session
from src.core.database.models import Review

# LoginScreen
class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self, text="Добро пожаловать!").pack(pady=10)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)
        tk.Button(self, text="Войти", command=self.handle_login).pack(pady=10)
        tk.Button(self, text="Регистрация", command=self.controller.show_register).pack()
    
    def handle_login(self):
        username = self.controller.username_entry.get().strip()
        password = self.controller.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните данные!")
            return
        auth = AuthManager()
        if auth.login(username, password):
            self.controller.on_login_success(username)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")


# RegisterScreen
class RegisterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self, text="Регистрация").pack(pady=10)
        frame = tk.Frame(self)
        frame.pack(pady=10)
        tk.Label(frame, text="Логин:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self, text="Зарегистрироваться", command=self.handle_register).pack(pady=10)
        tk.Button(self, text="Назад", command=self.controller.show_login).pack()
    
    def handle_register(self):
        username = self.username_entry.get().strip()
        password = self.username_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните данные!")
            return
        auth = AuthManager()
        try:
            auth.register(username, password)
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            self.controller.show_login()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))


# MainMenu
class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self, text="Главное меню").pack(pady=10)
        tk.Button(self, text="Просмотр отзывов", command=lambda: self.controller.show_screen(ReviewsScreen)).pack(pady=5)
        tk.Button(self, text="Сменить пароль", command=self.change_password).pack(pady=5)
        tk.Button(self, text="Выход", command=self.controller.logout).pack(pady=5)
    
    def change_password(self):
        messagebox.showinfo("Смена пароля", "Функция смены пароля\n(реализуйте по необходимости)")


# ReviewsScreen
class ReviewsScreen(tk.Frame):
    def __init__(self, parent, controller, mode='view'):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self, text="Просмотр отзывов").pack(pady=10)
        self.listbox = tk.Listbox(self, width=100)
        self.listbox.pack(pady=5, fill=tk.BOTH, expand=True)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Обновить", command=self.refresh_reviews).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Детальный отчёт", command=self.handle_report).pack(side=tk.LEFT, padx=5)
        if self.mode == 'write':
            tk.Button(btn_frame, text="Редактировать отзыв", command=self.handle_update).pack(side=tk.LEFT, padx=5)
        self.refresh_reviews()
    
    def refresh_reviews(self):
        session = Session()
        reviews = session.query(Review).all()
        self.listbox.delete(0, tk.END)
        for review in reviews:
            display = f"{review.id}: {review.title} - {review.final_score}/100 | Идея: {review.idea} ({review.idea_reason})"
            self.listbox.insert(tk.END, display)
        session.close()
    
    def handle_report(self):
        try:
            index = self.listbox.curselection()[0]
            review_id = int(self.listbox.get(index).split(":")[0])
        except IndexError:
            messagebox.showerror("Ошибка", "Выберите отзыв!")
            return
        from src.core.reports import generate_detailed_report
        session = Session()
        review = session.query(Review).filter(Review.id == review_id).first()
        session.close()
        if review:
            result = generate_detailed_report(review)
            messagebox.showinfo("Отчет", f"Данные отчёта собраны: {result}")
    
    def handle_update(self):
        try:
            index = self.listbox.curselection()[0]
            review_id = int(self.listbox.get(index).split(":")[0])
        except IndexError:
            messagebox.showerror("Ошибка", "Выберите отзыв для обновления!")
            return
        messagebox.showinfo("Редактирование", f"Редактирование отзыва {review_id}\n(реализуйте по необходимости)")
