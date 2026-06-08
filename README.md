🏥 Health Risk Prediction System

1. Project Title

Health Risk Prediction System

An AI-powered healthcare application that predicts a user's health risk level using machine learning techniques based on health parameters such as age, BMI, blood pressure, glucose level, and heart rate.

---

2. Problem Statement

In today's healthcare environment, identifying potential health risks at an early stage is difficult without continuous monitoring and medical expertise. Manual analysis of health data can be time-consuming and may not provide quick insights.

The Health Risk Prediction System uses Machine Learning algorithms to analyze user health parameters and predict risk levels automatically. This helps users take preventive measures and improve healthcare decision-making.

---

3. Project Objectives

Primary Objectives

- Predict health risks using Machine Learning algorithms.
- Analyze user health parameters efficiently.
- Provide early warnings for potential health issues.
- Generate health reports for users.
- Improve healthcare awareness through data-driven insights.

Secondary Objectives

- Maintain user health records.
- Enable future integration with healthcare systems.
- Improve prediction accuracy through advanced models.
- Support continuous health monitoring.

---

4. Module List

Module ID| Module Name| Description
M1| User Registration| Allows users to create an account
M2| User Login| Authenticates users securely
M3| Health Data Entry| Collects health parameters
M4| Risk Prediction| Predicts health risks using Machine Learning
M5| Report Generation| Generates and displays health reports
M6| Health Record Management| Stores and manages health history

---

5. Existing System

Existing System Issues
Manual health assessment
Time-consuming analysis
Delayed risk identification
Limited automation
Lack of predictive insights

---

6. Proposed System

The proposed Health Risk Prediction System uses Artificial Intelligence and Machine Learning techniques to analyze health-related data and predict possible health risks automatically.

Features

- Automated health risk prediction
- Fast and accurate analysis
- User-friendly interface
- Health report generation
- Secure data storage

---

7. Table List

User Table

Field Name| Data Type
user_id| INT
name| VARCHAR
email| VARCHAR
password| VARCHAR
age| INT
gender| VARCHAR

Health_Record Table

Field Name| Data Type
record_id| INT
user_id| INT
bmi| FLOAT
blood_pressure| INT
glucose_level| INT
heart_rate| INT
date| DATE

Prediction Table

Field Name| Data Type
prediction_id| INT
record_id| INT
risk_level| VARCHAR
prediction_date| DATE

---

8. Use Case Diagram

Actor

👤 User

Functionalities

- Register
- Login
- Enter Health Data
- Predict Health Risk
- View Health Report

---

9. ER Diagram

Entities

- USER
- HEALTH_RECORD
- PREDICTION

Relationships

- USER → HEALTH_RECORD (1:M)
- HEALTH_RECORD → PREDICTION (1:1)

---

10. Technology Stack

Category| Technology
Frontend| HTML, CSS, JavaScript
Backend| Python, Flask
Database| SQLite
Machine Learning| Scikit-learn
Data Processing| Pandas, NumPy
Development Tool| VS Code

---

11. Software Requirements

Component| Technology
Operating System| Windows 10/11
Programming Language| Python
Framework| Flask
Database| SQLite
IDE| VS Code

---

12. Hardware Requirements

Component| Specification
Processor| Intel i5 or above
RAM| 8 GB Minimum
Storage| 20 GB Free Space
Internet| Required

---

13. Future Enhancements

- Mobile Application Support
- Real-Time Health Monitoring
- Doctor Recommendation System
- Cloud-Based Data Storage
- Advanced AI Prediction Models
- Integration with Wearable Devices

---

14. Source Reference

Digital Healthcare – Hack-NU-thon 6.0

Nirma University, Ahmedabad

---

15. Author

Ayisha Suhaina S

B.Tech Artificial Intelligence and Data Science

Mini Project – Health Risk Prediction System
