from pathlib import Path
import pickle
import numpy as np

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "distress_model.pkl"
SCALER_PATH = Path(__file__).resolve().parent.parent / "models" / "scaler.pkl"

def _load_model():
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        return None, None
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    return model, scaler

def calculate_distress(mood, stress, sleep, activity, text_indicator=5.0):
    """
    Inputs are 1-10. Higher mood/activity/sleep values are positive,
    while higher stress is concerning. This prototype transforms them
    into a simple learned risk score.
    """
    model, scaler = _load_model()

    # Convert positive dimensions into concern-oriented dimensions.
    concern_mood = 11 - mood
    concern_sleep = 11 - sleep
    concern_activity = 11 - activity

    features = np.array([[
        concern_mood, stress, concern_sleep, concern_activity, text_indicator
    ]], dtype=float)

    if model is not None:
        scaled = scaler.transform(features)
        probability = float(model.predict_proba(scaled)[0][1])
        distress_score = round(probability * 100, 1)
    else:
        raw = (
            concern_mood * 0.25 +
            stress * 0.30 +
            concern_sleep * 0.20 +
            concern_activity * 0.15 +
            text_indicator * 0.10
        )
        distress_score = round(min(100, max(0, raw * 10)), 1)

    if distress_score < 35:
        risk = "Low Concern"
    elif distress_score < 65:
        risk = "Needs Attention"
    else:
        risk = "Human Review"

    return distress_score, risk
