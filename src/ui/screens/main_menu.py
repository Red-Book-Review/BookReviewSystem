import tkinter as tk
from tkinter import messagebox

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Главное меню").pack(pady=10)
        tk.Button(self, text="Выход", command=self.controller.logout).pack(pady=5)
        # ...other menu items as needed...
