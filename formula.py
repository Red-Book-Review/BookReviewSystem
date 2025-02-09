def calculate_final_score(idea, style, plot, emotion, influence, weights):
    """
    Улучшенная формула расчета оценки:
    1. Базовый расчет с весами (max 85 баллов)
    2. Штраф за низкие оценки (до -15 баллов)
    3. Бонус за влияние (до +15 баллов)
    """
    # Базовая оценка (максимум 85)
    base_score = (
        (idea * weights["idea"] + 
         style * weights["style"] + 
         plot * weights["plot"] + 
         emotion * weights["emotion"]) / 
        (weights["idea"] + weights["style"] + weights["plot"] + weights["emotion"])
    ) * 4.25  # 4.25 чтобы максимум был 85

    # Штраф за низкие оценки (чем ниже минимальная оценка, тем больше штраф)
    min_score = min(idea, style, plot, emotion)
    penalty = (20 - min_score) * 0.75  # максимальный штраф 15 баллов

    # Бонус за влияние (максимум 15 баллов)
    influence_bonus = (influence / 20) * 15

    # Итоговая оценка
    final_score = base_score - penalty + influence_bonus

    # Ограничиваем результат диапазоном [0, 100]
    return max(0, min(100, final_score))
