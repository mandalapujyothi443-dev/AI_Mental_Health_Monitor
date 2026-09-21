def score(value, field_name):
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a number.")
    if not 1 <= value <= 10:
        raise ValueError(f"{field_name} must be between 1 and 10.")
    return value
