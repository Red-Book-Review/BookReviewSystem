import tkinter as tk
from tkinter import ttk, messagebox
from src.core.config import APP_CONFIG  # changed to absolute import
from src.ui.screens import LoginScreen, RegisterScreen, MainMenu, ReviewsScreen  # using centralized exports
from src.ui.main import MainFrame  # unchanged if MainFrame exists in main.py

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Book Review System")
        self.geometry("800x600")
        self.mainframe = MainFrame(self)
        self.mainframe.pack(fill="both", expand=True)
