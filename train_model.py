import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)

# -----------------------------
# DATASET GENERATION
# -----------------------------

np.random.seed(42)

records = []

for _ in range(1000):

    glucose = np.random.randint(70, 250)
    haemoglobin = round(np.random.uniform(8, 18), 1)
    cholesterol = np.random.randint(120, 300)

    # Risk Classification Logic

    if (
        glucose < 110
        and haemoglobin > 13
        and cholesterol < 180
    ):
        risk = "Low Risk"

    elif (
        glucose > 180
        or haemoglobin < 10
        or cholesterol > 240
    ):
        risk = "High Risk"

    else:
        risk = "Medium Risk"

    records.append([
        glucose,
        haemoglobin,
        cholesterol,
        risk
    ])

# Create DataFrame

df = pd.DataFrame(
    records,
    columns=[
        "glucose",
        "haemoglobin",
        "cholesterol",
        "risk_level"
    ]
)

# Save Dataset

df.to_csv(
    "dataset/healthcare_data.csv",
    index=False
)

print("Dataset Generated Successfully")
print(df.head())

# -----------------------------
# PREPROCESSING
# -----------------------------

X = df[
    [
        "glucose",
        "haemoglobin",
        "cholesterol"
    ]
]

y = df["risk_level"]

# -----------------------------
# TRAIN TEST SPLIT
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -----------------------------
# MODEL TRAINING
# -----------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# -----------------------------
# EVALUATION
# -----------------------------

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\nModel Accuracy:")
print(f"{accuracy*100:.2f}%")

print("\nConfusion Matrix:")
print(confusion_matrix(
    y_test,
    y_pred
))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred
    )
)

# -----------------------------
# SAVE MODEL
# -----------------------------

with open(
    "model.pkl",
    "wb"
) as file:
    pickle.dump(
        model,
        file
    )

print("\nModel Saved Successfully")
print("File Name: model.pkl")