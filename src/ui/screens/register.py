import tkinter as tk
from tkinter import messagebox
from core.auth import AuthManager

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
        password = self.password_entry.get().strip()
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
