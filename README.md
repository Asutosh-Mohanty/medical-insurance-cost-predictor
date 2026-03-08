# AI Medical Insurance Cost Predictor

This project predicts medical insurance charges using Machine Learning.

## Model Details

Algorithm Used: Random Forest Regressor
Problem Type: Regression
Target Variable: Medical Insurance Charges

Model Evaluation
Metric	Value
R² Score	~0.87
Mean Absolute Error	~4181

The Random Forest model was selected after comparing multiple regression algorithms for optimal predictive performance.

## How to Run the Project
1️⃣ Clone the Repository
git clone https://github.com/Asutosh-Mohanty/medical-insurance-cost-predictor.git
cd medical-insurance-cost-predictor

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Train the Model (Run Once)
python model_training.py

This generates:

insurance_model.pkl → trained ML model

model_features.pkl → saved feature structure

model_score.json → evaluation metrics

4️⃣ Run the Application
streamlit run app.py

The application will open automatically in your browser.

## Project Structure
medical-insurance-cost-predictor/
│
├── app.py                    # Streamlit web application
├── model_training.py        # Machine learning training pipeline
├── insurance.csv            # Dataset
├── insurance_model.pkl      # Trained ML model
├── model_features.pkl       # Feature configuration
├── model_score.json         # Model evaluation metrics
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
└── screenshot/              # Application UI screenshots

## Tech Stack
- Python
- Scikit-learn
- Pandas
- Streamlit
- Plotly

## Features of the Application

🔍 Predict individual medical insurance costs

📈 Visualize risk factors affecting insurance pricing

📊 Interactive analytics and data visualizations

⚡ Fast predictions using a trained ML model

🌐 User-friendly Streamlit interface

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