def classify_trend(scores):
    if len(scores) < 2:
        return "Not enough history"

    recent = scores[-3:]
    if len(recent) >= 2:
        change = recent[-1] - recent[0]
        if change >= 10:
            return "Increasing concern"
        if change <= -10:
            return "Decreasing concern"
    return "Relatively stable"
