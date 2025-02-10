import matplotlib.pyplot as plt
from datetime import datetime

def generate_detailed_report(review):
    # Соберите данные отчёта
    report_data = {
        "title": review.title,
        "author": review.author,
        "review_date": review.review_date,
        "evaluator": review.evaluator,
        "details": {
           "idea": review.idea,
           "idea_reason": review.idea_reason,
           "style": review.style,
           "style_reason": review.style_reason,
           "plot": review.plot,
           "plot_reason": review.plot_reason,
           "emotion": review.emotion,
           "emotion_reason": review.emotion_reason,
           "influence": review.influence,
           "influence_reason": review.influence_reason
        },
        "final_score": review.final_score
    }
    # Вместо записи в файл – сохраните report_data в базу данных или верните его для дальнейшей обработки
    return report_data  # или вызов функции для сохранения в БД

def create_review_chart(review, save_path=None):
    labels = ['Идея', 'Стиль', 'Сюжет', 'Эмоции', 'Влияние']
    scores = [review.idea, review.style, review.plot, review.emotion, review.influence]
    colors = ['#2196f3', '#4caf50', '#f44336', '#9c27b0', '#ff9800']
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, scores, color=colors)
    plt.title(f'Оценки книги "{review.title}"')
    plt.ylabel('Баллы')
    plt.ylim(0, 20)
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom')
    if save_path:
        plt.savefig(save_path)
        plt.close()
        return save_path
    else:
        plt.show()
        plt.close()
        return None
