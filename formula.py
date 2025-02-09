def calculate_final_score(idea, style, plot, emotion, influence, weights):
    M = 20
    # ...вычисляем баллы по критериям...
    S_idea = (idea / M) * weights["idea"]
    S_style = (style / M) * weights["style"]
    S_plot = (plot / M) * weights["plot"]
    S_emotion = (emotion / M) * weights["emotion"]
    base_score = S_idea + S_style + S_plot + S_emotion
    bonus = (influence / M) * weights["influence"]
    scores = {"idea": S_idea, "style": S_style, "plot": S_plot, "emotion": S_emotion}
    min_score = min(scores.values())
    # Расчёт штрафа: если оценка главного критерия ниже максимума
    penalty = 1.0 + ((1 - min_score) / 1) * 2 if min_score < 1 else 1.0
    R = max(0, base_score * penalty)
    base_score_max = weights["idea"] + weights["style"] + weights["plot"] + weights["emotion"]
    normalized_score = (R / base_score_max) * 100
    normalized_score_with_bonus = normalized_score + (bonus * 100)
    return min(normalized_score_with_bonus, 100)
