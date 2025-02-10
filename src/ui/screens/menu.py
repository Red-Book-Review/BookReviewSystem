from tkinter import *
from tkinter import ttk
# Исправляем импорт на абсолютный
from src.core.config import MENU_ITEMS

class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Заголовок
        header = ttk.Label(
            self, 
            text=f"Главное меню | Пользователь: {self.controller.current_user}",
            style='Header.TLabel'
        )
        header.pack(pady=10)

        # Контейнер для кнопок с прокруткой
        canvas = Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        buttons_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Создаем кнопки меню
        for text, command in MENU_ITEMS:
            ttk.Button(
                buttons_frame,
                text=text,
                command=lambda cmd=command: self.controller.handle_menu_action(cmd),
                width=25
            ).pack(pady=3)
            
        canvas.create_window((0, 0), window=buttons_frame, anchor=NW)
        buttons_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=RIGHT, fill=Y)
