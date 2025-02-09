def calculate_final_score(idea, style, plot, emotion, influence, weights):
    M = 20
    # Расчет для основных критериев
    S_idea    = (idea / M) * weights["idea"]
    S_style   = (style / M) * weights["style"]
    S_plot    = (plot / M) * weights["plot"]
    S_emotion = (emotion / M) * weights["emotion"]
    
    base_score = S_idea + S_style + S_plot + S_emotion
    bonus = (influence / M) * weights["influence"]
    
    scores = {
        "idea":    S_idea,
        "style":   S_style,
        "plot":    S_plot,
        "emotion": S_emotion
    }
    avg_score = sum(scores.values()) / len(scores)
    min_score = min(scores.values())
    
    # Определяем, какой критерий имеет минимальное значение
    min_criterion = min(scores, key=scores.get)
    # Находим критерий с наибольшим весом среди основных
    sorted_weights = sorted(
        {k: weights[k] for k in ["idea", "style", "plot", "emotion"]}.items(),
        key=lambda x: x[1],
        reverse=True
    )
    main_criterion = sorted_weights[0][0]
    
    # Штраф рассчитывается сильнее, если минимальный критерий совпадает с ключевым
    main_penalty = (avg_score - min_score) * (2 if min_criterion == main_criterion else 1.5)
    
    R = max(0, (base_score - main_penalty) + bonus)
    R_max = (weights["idea"] + weights["style"] + weights["plot"] + weights["emotion"]) + weights["influence"]
    
    normalized_score = (R / R_max) * 100
    return normalized_score
