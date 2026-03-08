# AI Medical Insurance Cost Predictor

This project predicts medical insurance charges using Machine Learning.

## Overview

**AI Medical Insurance Cost Predictor** is an interactive machine learning web application that estimates individual medical insurance charges based on demographic and lifestyle attributes such as **age, BMI, smoking status, region, and number of dependents**.

Users enter personal and health-related information through an intuitive **Streamlit dashboard**, and the system generates an instant insurance cost prediction powered by a **Random Forest Regression model**.

The application also includes **interactive analytics and visualizations** that help users understand how different risk factors influence insurance pricing.

---

## Features

- 🎯 **Accurate Predictions** — Random Forest regression model with **R² ≈ 0.87** on test data  
- 📊 **Interactive Dashboard** — Visual analytics for exploring insurance cost trends  
- ⚡ **Real-time Predictions** — Instant predictions using a trained machine learning model  
- 📈 **Data Visualization** — Interactive charts powered by **Plotly**  
- 🧠 **Machine Learning Pipeline** — Data preprocessing, training, evaluation, and deployment  
- 🧾 **User-friendly Interface** — Clean **Streamlit UI** for easy interaction  
- 🔍 **Risk Factor Analysis** — Understand how BMI, smoking, and age impact insurance costs

## Model Details

Algorithm Used: Random Forest Regressor
Problem Type: Regression
Target Variable: Medical Insurance Charges

Model Evaluation
Metric	Value
R² Score	~0.87
Mean Absolute Error	~4181

The Random Forest model was selected after comparing multiple regression algorithms for optimal predictive performance.
## 🚀 How to Run

### Step 1 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 2 — Train the Model (Run Once)

```bash
python model_training.py
```

This will generate:

* `insurance_model.pkl` → trained ML model
* `model_features.pkl` → saved feature structure
* `model_score.json` → evaluation metrics

---

### Step 3 — Start the Streamlit App

```bash
streamlit run app.py
```

---

### Step 4 — Open in Browser

The application will automatically open in your browser.

If it doesn't open, go to:

```
http://localhost:8501
```

## Application Screenshot

### Dashboard
<p align="center">
<img src="screenshot/Dashboard.png" width="800">
</p>

### Prediction Page
<p align="center">
<img src="screenshot/prediction.png" width="800">
</p>

### Risk Analysis
<p align="center">
<img src="screenshot/Cost_Trajectory.png" width="800">
</p>


## 📂 Project Structure

medical-insurance-cost-predictor/
│
├── app.py                   # Streamlit web application
├── model_training.py        # Machine learning training pipeline
├── insurance.csv            # Dataset used for training
│
├── insurance_model.pkl      # Trained ML model
├── model_features.pkl       # Saved feature configuration
├── model_score.json         # Model evaluation metrics
│
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
│
└── screenshot/              # Application UI screenshots
    ├── Dashboard.png
    ├── prediction.png
    └── Cost_Trajectory.png

## 🛠 Tech Stack

| Layer | Technology |
|------|------------|
| Backend | Python 3.10+, Streamlit |
| ML / Data | Scikit-learn, Pandas, NumPy |
| Data Visualization | Plotly |
| Dataset | Medical Insurance Dataset (`insurance.csv`) |
| Model Persistence | Python `pickle` |
| Development | VS Code |