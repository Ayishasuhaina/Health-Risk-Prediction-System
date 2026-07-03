CREATE TABLE User (
    user_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(100),
    age INT,
    gender VARCHAR(10)
);

CREATE TABLE Health_Record (
    record_id INT PRIMARY KEY,
    user_id INT,
    bmi FLOAT,
    blood_pressure INT,
    glucose_level INT,
    heart_rate INT,
    date DATE,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Prediction (
    prediction_id INT PRIMARY KEY,
    record_id INT,
    risk_level VARCHAR(20),
    prediction_date DATE,
    FOREIGN KEY (record_id) REFERENCES Health_Record(record_id)
);
