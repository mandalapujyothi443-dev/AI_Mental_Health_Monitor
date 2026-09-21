def text_indicator_score(text):
    if not text:
        return 5.0

    text = text.lower()
    high = ["overwhelmed", "panic", "terrified", "hopeless", "distress"]
    medium = ["stress", "stressed", "anxious", "worried", "sad", "lonely", "fear"]

    high_hits = sum(word in text for word in high)
    medium_hits = sum(word in text for word in medium)

    score = 5.0 + (high_hits * 1.5) + (medium_hits * 0.7)
    return min(10.0, score)
