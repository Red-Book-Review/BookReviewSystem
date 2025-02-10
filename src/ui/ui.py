import tkinter as tk
from tkinter import ttk, messagebox
from ..core.config import APP_CONFIG
from ui.screens.login import LoginScreen
from ui.screens.menu import MainMenu
from ui.screens.reviews import ReviewsScreen
from ui.screens.register import RegisterScreen

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.current_screen = None
        self.setup_window()
        self.show_login()

    def setup_window(self):
        self.title(APP_CONFIG['app_name'])
        self.geometry(APP_CONFIG['window_size'])
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

    def show_login(self):
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = LoginScreen(self.main_container, self)
        self.current_screen.pack(fill=tk.BOTH, expand=True)

    def show_register(self):
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = RegisterScreen(self.main_container, self)
        self.current_screen.pack(fill=tk.BOTH, expand=True)

    def on_login_success(self, username):
        self.current_user = username
        self.show_menu()

    def show_menu(self):
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = MainMenu(self.main_container, self)
        self.current_screen.pack(fill=tk.BOTH, expand=True)

    def show_screen(self, screen_class, **kwargs):
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = screen_class(self.main_container, self, **kwargs)
        self.current_screen.pack(fill=tk.BOTH, expand=True)

    def logout(self):
        if messagebox.askyesno("Выход", "Выйти из системы?"):
            self.current_user = None
            self.show_login()

    def on_close(self):
        if messagebox.askyesno("Выход", "Закрыть приложение?"):
            self.destroy()
