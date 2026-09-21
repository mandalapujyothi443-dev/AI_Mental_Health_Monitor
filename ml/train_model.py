from pathlib import Path
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "sample_data.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

FEATURES = [
    "concern_mood",
    "stress",
    "concern_sleep",
    "concern_activity",
    "text_indicator"
]

def train():
    df = pd.read_csv(DATA)
    X = df[FEATURES]
    y = df["target"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print("Accuracy:", round(accuracy_score(y_test, predictions), 3))
    print(classification_report(y_test, predictions))

    with open(MODEL_DIR / "distress_model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open(MODEL_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    print("Saved ML model and scaler.")

if __name__ == "__main__":
    train()
