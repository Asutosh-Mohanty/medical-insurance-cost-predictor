import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# Load dataset
data = pd.read_csv("insurance.csv")

# Encode categorical columns
data['sex'] = data['sex'].map({'male':1,'female':0})
data['smoker'] = data['smoker'].map({'yes':1,'no':0})

# Feature engineering
data["bmi_age"] = data["bmi"] * data["age"]
data["obese"] = (data["bmi"] >= 30).astype(int)

# One hot encoding
data = pd.get_dummies(data, columns=['region'], drop_first=True)

# Features & target
X = data.drop("charges", axis=1)
y = data["charges"]

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ═══════════════════════════════════════
# Linear Regression
# ═══════════════════════════════════════
lr = LinearRegression()
lr.fit(X_train, y_train)
lr_pred = lr.predict(X_test)

lr_r2 = r2_score(y_test, lr_pred)

# ═══════════════════════════════════════
# Random Forest (much stronger)
# ═══════════════════════════════════════
rf = RandomForestRegressor(
    n_estimators=500,
    max_depth=12,
    min_samples_split=5,
    random_state=42
)

rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)

rf_r2 = r2_score(y_test, rf_pred)

print("\nModel Performance\n")

print("Linear Regression R2:", lr_r2)
print("Random Forest R2:", rf_r2)

# Select best model
best_model = rf if rf_r2 > lr_r2 else lr

print("\nBest Model:", type(best_model).__name__)

# Save model
pickle.dump(best_model, open("insurance_model.pkl","wb"))

# Save feature order
pickle.dump(list(X.columns), open("model_features.pkl","wb"))

print("\nModel saved successfully!")
import json
with open("model_score.json", "w") as f:
    json.dump({"r2": round(rf_r2 if rf_r2 > lr_r2 else lr_r2, 4)}, f)
print("Score saved:", round(rf_r2 if rf_r2 > lr_r2 else lr_r2, 4))