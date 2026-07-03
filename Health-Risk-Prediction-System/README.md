# Health Risk Prediction System

## Project Overview

The **Health Risk Prediction System** is an AI-powered web application that predicts whether a user is at **Low Risk**, **Medium Risk**, or **High Risk** based on medical and lifestyle information. Built with Flask and Scikit-learn, it provides personalized health recommendations and downloadable PDF reports.

## Features

- **User Authentication** – Register, login, logout, forgot password, profile management
- **Role-Based Access** – Separate user and admin roles with secure session management
- **AI Prediction** – Multi-model ML pipeline with automatic best-model selection
- **Personalized Recommendations** – Lifestyle, diet, exercise, and medical advice
- **Dashboard Analytics** – Interactive Chart.js visualizations and monthly statistics
- **Prediction History** – View past assessments with detailed recommendations
- **PDF Reports** – Downloadable health risk reports
- **Admin Dashboard** – System-wide user, prediction, and feedback analytics
- **Feedback System** – User ratings and feedback collection
- **Responsive UI** – Modern Bootstrap 5 interface with gradient theme

## Folder Structure

```
Health-Risk-Prediction-System/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── dataset/
│   ├── generate_dataset.py # Synthetic dataset generator
│   └── health_risk_dataset.csv
├── model/
│   ├── preprocessing.py    # Data preprocessing pipeline
│   ├── train_model.py      # Model training and EDA
│   └── predict.py          # Prediction module
├── trained_model/
│   ├── model.pkl           # Best trained model
│   ├── scaler.pkl          # Feature scaler
│   └── label_encoders.pkl  # Categorical encoders
├── database/
│   └── database.db         # SQLite database
├── utils/
│   ├── database.py         # SQLAlchemy models
│   ├── helpers.py          # Utility functions
│   ├── validators.py       # Input validation
│   └── recommendations.py  # Health recommendations
├── templates/              # Jinja2 HTML templates
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   ├── images/             # EDA charts
│   └── reports/            # Generated PDF reports
```

## Installation

1. **Clone or download** the project folder.

2. **Create a virtual environment** (recommended):

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.9+
- Flask 3.0+
- Scikit-learn 1.5+
- Pandas, NumPy, Matplotlib, Seaborn
- Flask-SQLAlchemy, Flask-WTF
- ReportLab (PDF generation)
- Bootstrap 5, Chart.js (via CDN)

## How to Run

From the project root directory:

```bash
python app.py
```

On first run, the application will automatically:
1. Generate the synthetic dataset (15,000+ rows)
2. Train and compare 7 ML models
3. Save the best model and preprocessing artifacts
4. Initialize the SQLite database with a default admin account

Open your browser at: **http://localhost:5000**

### Default Admin Credentials

- **Username:** `admin`
- **Password:** `Admin@123`

## Dataset Information

The synthetic dataset contains **15,000+ records** with balanced classes:

| Column | Description |
|--------|-------------|
| Age | Patient age (18-85) |
| Gender | Male, Female, Other |
| Height | Height in cm |
| Weight | Weight in kg |
| BMI | Body Mass Index |
| SystolicBP | Systolic blood pressure |
| DiastolicBP | Diastolic blood pressure |
| HeartRate | Resting heart rate |
| BloodSugar | Blood sugar level (mg/dL) |
| Cholesterol | Cholesterol level (mg/dL) |
| Smoking | No, Occasionally, Yes |
| Alcohol | No, Occasionally, Yes |
| PhysicalActivity | Sedentary to Very Active |
| ExerciseFrequency | Never to Daily |
| DietQuality | Poor to Excellent |
| SleepHours | Hours of sleep |
| StressLevel | Low to Very High |
| FamilyHistory | No, Yes |
| Diabetes | No, Yes |
| HeartDisease | No, Yes |
| RiskLevel | Low Risk, Medium Risk, High Risk |

## Machine Learning Models

The system trains and compares the following algorithms:

1. Logistic Regression
2. Decision Tree
3. Random Forest
4. Gradient Boosting
5. K-Nearest Neighbors (KNN)
6. Naive Bayes
7. Support Vector Machine (SVM)

**Evaluation Metrics:** Accuracy, Precision, Recall, F1 Score, ROC AUC, Confusion Matrix

The best model is automatically selected based on a weighted combination of F1 score, ROC AUC, and accuracy.

## Screenshots

> Placeholder for application screenshots:
> - Landing Page
> - Prediction Form
> - Dashboard with Charts
> - Admin Panel
> - PDF Report Sample

## Future Scope

- Integration with wearable device APIs
- Real-time health monitoring dashboard
- Deep learning models (Neural Networks)
- Multi-language support
- Email notifications for high-risk predictions
- Telemedicine consultation booking
- Mobile application (React Native / Flutter)
- FHIR/HL7 healthcare data interoperability

## Author

**Health Risk Prediction System**
Developed as a production-ready AI healthcare application.

---

*Disclaimer: This application is for educational and informational purposes only. It does not replace professional medical advice.*
