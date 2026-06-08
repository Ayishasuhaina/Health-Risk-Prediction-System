# ER Diagram

USER
- user_id (PK)
- name
- email
- password
- age
- gender

HEALTH_RECORD
- record_id (PK)
- user_id (FK)
- bmi
- blood_pressure
- glucose_level
- heart_rate

PREDICTION
- prediction_id (PK)
- record_id (FK)
- risk_level
- prediction_date

Relationship:
USER → HEALTH_RECORD (1:M)
HEALTH_RECORD → PREDICTION (1:1)
