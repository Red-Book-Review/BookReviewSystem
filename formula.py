def calculate_final_score(idea, style, plot, emotion, influence, weights):
    # Вычисляем основной процент по критериям (максимум 100)
    main_total = idea * weights["idea"] + style * weights["style"] + plot * weights["plot"] + emotion * weights["emotion"]
    main_max = 20 * (weights["idea"] + weights["style"] + weights["plot"] + weights["emotion"])
    main_percentage = (main_total / main_max) * 100

    # Новый коэффициент штрафа: диапазон [0.7, 1.0] при вариациях минимального балла
    penalty = 0.7 + (0.3 * (min(idea, style, plot, emotion) / 20))
    penalized_score = main_percentage * penalty

    # Бонус сохраняется как раньше
    bonus_score = (influence / 20) * 100 * weights["influence"]

    final_score = penalized_score + bonus_score
    return min(final_score, 100)
