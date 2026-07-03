"""Model training, evaluation, and EDA visualization."""

import os
import sys
import warnings

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import label_binarize
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from config import Config
from model.preprocessing import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, DataPreprocessor, TARGET_COLUMN

IMAGES_DIR = Config.IMAGES_DIR


def ensure_image_dir():
    """Create directory for EDA images."""
    os.makedirs(IMAGES_DIR, exist_ok=True)


def detect_outliers_iqr(series):
    """Detect outliers using IQR method."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return ((series < lower) | (series > upper)).sum()


def run_eda(df):
    """Generate exploratory data analysis visualizations."""
    ensure_image_dir()
    sns.set_theme(style="whitegrid")

    for column in NUMERIC_COLUMNS[:6]:
        plt.figure(figsize=(8, 5))
        sns.histplot(df[column], kde=True, color="#4e73df")
        plt.title(f"Histogram of {column}")
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, f"hist_{column.lower()}.png"))
        plt.close()

    plt.figure(figsize=(12, 8))
    sns.boxplot(data=df[NUMERIC_COLUMNS[:8]], orient="h", palette="Set2")
    plt.title("Box Plot of Key Numeric Features")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "boxplot_features.png"))
    plt.close()

    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x="Age", y="BMI", hue="RiskLevel", palette="viridis", alpha=0.6)
    plt.title("Scatter Plot: Age vs BMI by Risk Level")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "scatter_age_bmi.png"))
    plt.close()

    plt.figure(figsize=(10, 8))
    correlation = df[NUMERIC_COLUMNS].corr()
    sns.heatmap(correlation, annot=False, cmap="coolwarm", linewidths=0.5)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "heatmap_correlation.png"))
    plt.close()

    sample_df = df.sample(n=min(500, len(df)), random_state=42)
    sns.pairplot(sample_df[NUMERIC_COLUMNS[:5] + [TARGET_COLUMN]], hue=TARGET_COLUMN, corner=True)
    plt.savefig(os.path.join(IMAGES_DIR, "pairplot.png"))
    plt.close()

    plt.figure(figsize=(7, 7))
    risk_counts = df[TARGET_COLUMN].value_counts()
    plt.pie(risk_counts, labels=risk_counts.index, autopct="%1.1f%%", startangle=140,
            colors=["#1cc88a", "#f6c23e", "#e74a3b"])
    plt.title("Risk Level Distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "pie_risk_distribution.png"))
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x="Smoking", hue="RiskLevel", palette="muted")
    plt.title("Count Plot: Smoking vs Risk Level")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "countplot_smoking.png"))
    plt.close()

    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation, annot=True, fmt=".2f", cmap="RdYlBu_r")
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "correlation_matrix.png"))
    plt.close()

    outlier_report = {column: detect_outliers_iqr(df[column]) for column in NUMERIC_COLUMNS}
    outlier_df = pd.DataFrame(list(outlier_report.items()), columns=["Feature", "OutlierCount"])
    plt.figure(figsize=(10, 6))
    sns.barplot(data=outlier_df, x="Feature", y="OutlierCount", palette="Reds_r")
    plt.title("Outlier Detection (IQR Method)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "outlier_detection.png"))
    plt.close()


def get_models():
    """Return dictionary of models to train and compare."""
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=12),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=7),
        "Naive Bayes": GaussianNB(),
        "Support Vector Machine": SVC(kernel="rbf", probability=True, random_state=42),
    }


def evaluate_model(model, x_test, y_test, target_names):
    """Compute comprehensive evaluation metrics."""
    y_pred = model.predict(x_test)
    y_proba = model.predict_proba(x_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average="weighted"),
        "recall": recall_score(y_test, y_pred, average="weighted"),
        "f1": f1_score(y_test, y_pred, average="weighted"),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "report": classification_report(y_test, y_pred, target_names=target_names),
    }

    y_test_bin = label_binarize(y_test, classes=np.arange(len(target_names)))
    if y_test_bin.shape[1] == len(target_names):
        metrics["roc_auc"] = roc_auc_score(y_test_bin, y_proba, multi_class="ovr", average="weighted")
    else:
        metrics["roc_auc"] = 0.0

    return metrics


def plot_feature_importance(model, feature_names):
    """Plot feature importance for tree-based models."""
    if not hasattr(model, "feature_importances_"):
        return

    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1][:15]

    plt.figure(figsize=(10, 6))
    plt.bar(range(len(indices)), importance[indices], color="#36b9cc")
    plt.xticks(range(len(indices)), [feature_names[i] for i in indices], rotation=45, ha="right")
    plt.title("Feature Importance")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "feature_importance.png"))
    plt.close()


def plot_confusion_matrix(cm, target_names, title="Confusion Matrix"):
    """Save confusion matrix visualization."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=target_names, yticklabels=target_names)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "confusion_matrix_best.png"))
    plt.close()


def train_and_select_best_model():
    """Train all models, compare metrics, and save the best performer."""
    preprocessor = DataPreprocessor()
    df = preprocessor.load_data()
    run_eda(df)

    x_train, x_test, y_train, y_test, _ = preprocessor.prepare_training_data(df)
    target_names = list(preprocessor.target_encoder.classes_)

    results = []
    best_model = None
    best_name = ""
    best_score = -1.0
    best_metrics = None

    for name, model in get_models().items():
        model.fit(x_train, y_train)
        metrics = evaluate_model(model, x_test, y_test, target_names)
        cv_score = cross_val_score(model, x_train, y_train, cv=5, scoring="f1_weighted").mean()

        results.append({
            "Model": name,
            "Accuracy": round(metrics["accuracy"], 4),
            "Precision": round(metrics["precision"], 4),
            "Recall": round(metrics["recall"], 4),
            "F1 Score": round(metrics["f1"], 4),
            "ROC AUC": round(metrics["roc_auc"], 4),
            "CV F1": round(cv_score, 4),
        })

        combined_score = metrics["f1"] * 0.4 + metrics["roc_auc"] * 0.3 + metrics["accuracy"] * 0.3
        if combined_score > best_score:
            best_score = combined_score
            best_model = model
            best_name = name
            best_metrics = metrics

    comparison_df = pd.DataFrame(results)
    comparison_df.to_csv(os.path.join(BASE_DIR, "trained_model", "model_comparison.csv"), index=False)

    plt.figure(figsize=(12, 6))
    melted = comparison_df.melt(id_vars="Model", value_vars=["Accuracy", "Precision", "Recall", "F1 Score", "ROC AUC"])
    sns.barplot(data=melted, x="Model", y="value", hue="variable", palette="Set2")
    plt.title("Model Comparison Metrics")
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "model_comparison.png"))
    plt.close()

    os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)
    joblib.dump(best_model, Config.MODEL_PATH)
    preprocessor.save_artifacts()

    plot_confusion_matrix(best_metrics["confusion_matrix"], target_names, f"Best Model: {best_name}")
    plot_feature_importance(best_model, preprocessor.feature_columns)

    print(f"Best model selected: {best_name}")
    print(comparison_df.to_string(index=False))
    print(best_metrics["report"])

    return best_name, comparison_df


if __name__ == "__main__":
    dataset_path = Config.DATASET_PATH
    if not os.path.exists(dataset_path):
        from dataset.generate_dataset import main as generate_main
        generate_main()
    train_and_select_best_model()
