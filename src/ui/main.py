import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.core.config import APP_CONFIG
from src.ui.screens import LoginScreen, RegisterScreen, MainMenu, ReviewsScreen  # using centralized exports

class MainFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.username_entry = None
        self.password_entry = None
        self.show_login()

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        # Pass self as controller
        self.current_screen = LoginScreen(self, self)
        self.current_screen.pack(fill="both", expand=True)

    def show_register(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.current_screen = RegisterScreen(self, self)
        self.current_screen.pack(fill="both", expand=True)

    def on_login_success(self, username):
        for widget in self.winfo_children():
            widget.destroy()
        self.current_screen = MainMenu(self, self)
        self.current_screen.pack(fill="both", expand=True)

    def logout(self):
        self.show_login()


class Application:
    def __init__(self):
        self.root = tk.Tk()  # use tk.Tk() instead of Tk()
        self.setup_window()
        self.current_screen = None
        self.show_login()

    def setup_window(self):
        """Настройка главного окна"""
        self.root.title(APP_CONFIG['app_name'])
        self.root.geometry(APP_CONFIG['window_size'])
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Создаем главный контейнер using tk.BOTH if needed
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

    def show_login(self):
        """Показ экрана входа"""
        if self.current_screen:
            self.current_screen.destroy()
        # Pass self as controller along with the on_login callback
        self.current_screen = LoginScreen(self.main_container, self, on_login=self.on_login_success)
    
    def on_login_success(self, username):
        """Callback успешного входа"""
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = ReviewsScreen(self.main_container, self, mode='view', username=username, on_logout=self.show_login)
    
    def on_close(self):
        """Обработка закрытия окна"""
        if messagebox.askokcancel("Выход", "Закрыть приложение?"):
            self.root.quit()

def main():
    app = Application()
    app.root.mainloop()

if __name__ == "__main__":
    main()
