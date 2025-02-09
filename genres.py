# Словарь жанров и их весов
genre_weights = {
    "фантастика": {"idea": 0.35, "style": 0.20, "plot": 0.25, "emotion": 0.15, "influence": 0.05},
    "детектив": {"idea": 0.20, "style": 0.20, "plot": 0.40, "emotion": 0.10, "influence": 0.10},
    "романтика": {"idea": 0.15, "style": 0.25, "plot": 0.20, "emotion": 0.30, "influence": 0.10},
    "поэзия": {"idea": 0.10, "style": 0.30, "plot": 0.10, "emotion": 0.40, "influence": 0.10},
    "научная литература": {"idea": 0.25, "style": 0.20, "plot": 0.25, "emotion": 0.15, "influence": 0.15},
    "безжанровый": {}  # В этом случае веса указываются вручную
}

def get_genre_weights(genre):
    return genre_weights.get(genre.lower())
    
# ...возможно добавить функции для динамического обновления или сохранения настроек жанров...
