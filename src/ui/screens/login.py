import tkinter as tk
from tkinter import messagebox
from src.core.auth import AuthManager  # changed from relative import

class LoginScreen(tk.Frame):
    def __init__(self, parent, controller, on_login=None):
        super().__init__(parent)
        # Use the provided callback or fallback to the controller's method
        self.on_login = on_login if on_login is not None else controller.on_login_success
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
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните данные!")
            return
        auth = AuthManager()
        if auth.login(username, password):
            self.on_login(username)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
