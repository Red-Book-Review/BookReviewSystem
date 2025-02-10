import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Используем абсолютные импорты
from src.core.database.connection import Session  # absolute import
from src.core.database.models import Review        # absolute import

class ReviewsScreen(tk.Frame):
    def __init__(self, parent, controller, mode='view', username=None, on_logout=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.username = username
        self.on_logout = on_logout
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
            display = f"{review.id}: {review.title} - {review.final_score}/100 | " \
                      f"Идея: {review.idea} ({review.idea_reason})"
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
            filename = generate_detailed_report(review)
            messagebox.showinfo("Отчет", f"Отчёт сохранен: {filename}")

    def handle_update(self):
        # Пример вызова обновления отзыва
        try:
            index = self.listbox.curselection()[0]
            review_id = int(self.listbox.get(index).split(":")[0])
        except IndexError:
            messagebox.showerror("Ошибка", "Выберите отзыв для обновления!")
            return
        # Здесь можно открыть окно для редактирования
        messagebox.showinfo("Редактирование", f"Редактирование отзыва {review_id}")
        # Для примера вызываем метод обновления из AuthManager (или отдельного менеджера)
        # auth = AuthManager()
        # auth.update_review(review_id, title="Новое название", ...)
