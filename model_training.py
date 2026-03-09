import pandas as pd
import numpy as np
import pickle
import json
import os

from sklearn.model_selection import train_test_split
from sklearn.linear_model    import LinearRegression
from sklearn.ensemble        import RandomForestRegressor
from sklearn.metrics         import r2_score, mean_absolute_error

# All files saved in the SAME folder as train.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_csv():
    for p in [
        os.path.join(BASE_DIR, "insurance.csv"),
        os.path.join(BASE_DIR, "data", "insurance.csv"),
    ]:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "\n❌  insurance.csv not found."
        "\n    Place it in the same folder as train.py:"
        f"\n    👉  {BASE_DIR}\\"
    )

print("\n📂  Loading dataset ...")
data = pd.read_csv(find_csv())
print(f"    {len(data):,} rows loaded.")

data["sex"]    = data["sex"].map({"male":1,"female":0})
data["smoker"] = data["smoker"].map({"yes":1,"no":0})
data["bmi_age"] = data["bmi"] * data["age"]
data["obese"]   = (data["bmi"] >= 30).astype(int)
data = pd.get_dummies(data, columns=["region"], drop_first=True)

X = data.drop("charges", axis=1)
y = data["charges"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"    Train: {len(X_train):,}  |  Test: {len(X_test):,}")

print("\n🔁  Training Linear Regression ...")
lr = LinearRegression()
lr.fit(X_train, y_train)
lr_r2 = r2_score(y_test, lr.predict(X_test))
print(f"    R2 = {lr_r2:.4f}")

print("\n🌲  Training Random Forest (may take ~30s) ...")
rf = RandomForestRegressor(n_estimators=500, max_depth=12,
                           min_samples_split=5, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
rf_r2  = r2_score(y_test, rf.predict(X_test))
rf_mae = mean_absolute_error(y_test, rf.predict(X_test))
print(f"    R2 = {rf_r2:.4f}   MAE = ${rf_mae:,.0f}")

best_model = rf if rf_r2 > lr_r2 else lr
best_r2    = rf_r2 if rf_r2 > lr_r2 else lr_r2
best_mae   = rf_mae if rf_r2 > lr_r2 else mean_absolute_error(y_test, lr.predict(X_test))
best_name  = type(best_model).__name__

print(f"\n{'='*42}")
print(f"  Best : {best_name}")
print(f"  R2   : {best_r2:.4f}")
print(f"  MAE  : ${best_mae:,.0f}")
print(f"{'='*42}")

# Save everything to the SAME folder as train.py
pickle.dump(best_model,      open(os.path.join(BASE_DIR, "insurance_model.pkl"), "wb"))
pickle.dump(list(X.columns), open(os.path.join(BASE_DIR, "model_features.pkl"), "wb"))
with open(os.path.join(BASE_DIR, "model_score.json"), "w") as f:
    json.dump({"r2": round(best_r2,4), "mae": round(best_mae,2), "model": best_name}, f, indent=2)

print("\n  Saved:")
print(f"  insurance_model.pkl  -->  {BASE_DIR}")
print(f"  model_features.pkl   -->  {BASE_DIR}")
print(f"  model_score.json     -->  {BASE_DIR}")
print("\n  Now run:  streamlit run app.py\n")
