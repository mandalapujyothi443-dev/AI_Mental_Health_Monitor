import pandas as pd

FEATURES = [
    "concern_mood",
    "stress",
    "concern_sleep",
    "concern_activity",
    "text_indicator"
]

def load_and_prepare(path):
    df = pd.read_csv(path)
    X = df[FEATURES].copy()
    y = df["target"].astype(int)
    return X, y
