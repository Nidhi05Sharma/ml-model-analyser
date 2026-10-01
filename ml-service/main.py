from fastapi import FastAPI, UploadFile, File, Form
import pandas as pd
import time

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC

from sklearn.cluster import KMeans

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "ML Model Analyzer ML Service is running"
    }


@app.post("/train")
async def train_model(
    file: UploadFile = File(...),
    learning_type: str = Form(...),
    problem_type: str = Form(None),
    model: str = Form(...)
):

    # Read CSV
    df = pd.read_csv(file.file)

    # Remove completely empty columns
    df = df.dropna(axis=1, how="all")

    # Remove duplicate rows
    df = df.drop_duplicates()

    # =====================================================
    # MODEL DEFINITIONS
    # =====================================================

    classification_models = {
        "logistic_regression": LogisticRegression(
            max_iter=500
        ),

        "decision_tree": DecisionTreeClassifier(
            max_depth=10,
            random_state=42
        ),

        "random_forest": RandomForestClassifier(
            n_estimators=20,
            max_depth=10,
            random_state=42,
            n_jobs=1
        ),

        "svm": SVC()
    }

    regression_models = {
        "linear_regression": LinearRegression(),

        "decision_tree_regressor": DecisionTreeRegressor(
            max_depth=10,
            random_state=42
        ),

        "random_forest_regressor": RandomForestRegressor(
            n_estimators=20,
            max_depth=10,
            random_state=42,
            n_jobs=1
        )
    }

    unsupervised_models = {
        "kmeans": KMeans(
            n_clusters=3,
            random_state=42,
            n_init=10
        )
    }

    # =====================================================
    # VALIDATE LEARNING TYPE
    # =====================================================

    if learning_type not in ["supervised", "unsupervised"]:
        return {
            "error": "Invalid learning type.",
            "available_learning_types": [
                "supervised",
                "unsupervised"
            ]
        }

    # =====================================================
    # SUPERVISED
    # =====================================================

    if learning_type == "supervised":

        if problem_type not in [
            "classification",
            "regression"
        ]:
            return {
                "error": "Invalid problem type.",
                "available_problem_types": [
                    "classification",
                    "regression"
                ]
            }

        # -----------------------------
        # CLASSIFICATION
        # -----------------------------

        if problem_type == "classification":

            if model not in classification_models:
                return {
                    "error": "Invalid classification model.",
                    "available_models": list(
                        classification_models.keys()
                    )
                }

            selected_model = classification_models[model]

        # -----------------------------
        # REGRESSION
        # -----------------------------

        else:

            if model not in regression_models:
                return {
                    "error": "Invalid regression model.",
                    "available_models": list(
                        regression_models.keys()
                    )
                }

            selected_model = regression_models[model]

        # =================================================
        # TARGET
        # =================================================

        target_column = df.columns[-1]

        X = df.drop(columns=[target_column])
        y = df[target_column]

        # Remove ID-like columns
        id_columns = []

        for column in X.columns:

            if X[column].nunique() == len(X):
                id_columns.append(column)

        if id_columns:
            X = X.drop(columns=id_columns)

        # Identify column types
        numerical_columns = X.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()

        categorical_columns = X.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # Numerical preprocessing
        numerical_transformer = Pipeline([
            ("scaler", StandardScaler())
        ])

        # Categorical preprocessing
        categorical_transformer = OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=True
        )

        # Combined preprocessing
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numerical",
                    numerical_transformer,
                    numerical_columns
                ),
                (
                    "categorical",
                    categorical_transformer,
                    categorical_columns
                )
            ]
        )

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        # Create pipeline
        pipeline = Pipeline([
            ("preprocessing", preprocessor),
            ("model", selected_model)
        ])

        # =================================================
        # TRAINING
        # =================================================

        start_time = time.perf_counter()

        pipeline.fit(X_train, y_train)

        training_time = time.perf_counter() - start_time

        # =================================================
        # PREDICTION
        # =================================================

        start_time = time.perf_counter()

        predictions = pipeline.predict(X_test)

        prediction_time = time.perf_counter() - start_time

        # =================================================
        # CLASSIFICATION METRICS
        # =================================================

        if problem_type == "classification":

            accuracy = accuracy_score(
                y_test,
                predictions
            )

            precision = precision_score(
                y_test,
                predictions,
                average="weighted",
                zero_division=0
            )

            recall = recall_score(
                y_test,
                predictions,
                average="weighted",
                zero_division=0
            )

            f1 = f1_score(
                y_test,
                predictions,
                average="weighted",
                zero_division=0
            )

            return {
                "learning_type": "supervised",
                "problem_type": "classification",
                "model": model,
                "filename": file.filename,
                "rows": len(df),
                "features": len(X.columns),
                "target": target_column,
                "removed_id_columns": id_columns,
                "results": {
                    "accuracy": round(accuracy, 4),
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                    "f1": round(f1, 4),
                    "training_time": round(
                        training_time,
                        6
                    ),
                    "prediction_time": round(
                        prediction_time,
                        6
                    )
                }
            }

        # =================================================
        # REGRESSION METRICS
        # =================================================

        else:

            mae = mean_absolute_error(
                y_test,
                predictions
            )

            mse = mean_squared_error(
                y_test,
                predictions
            )

            rmse = mse ** 0.5

            r2 = r2_score(
                y_test,
                predictions
            )

            return {
                "learning_type": "supervised",
                "problem_type": "regression",
                "model": model,
                "filename": file.filename,
                "rows": len(df),
                "features": len(X.columns),
                "target": target_column,
                "removed_id_columns": id_columns,
                "results": {
                    "mae": round(mae, 4),
                    "mse": round(mse, 4),
                    "rmse": round(rmse, 4),
                    "r2": round(r2, 4),
                    "training_time": round(
                        training_time,
                        6
                    ),
                    "prediction_time": round(
                        prediction_time,
                        6
                    )
                }
            }

    # =====================================================
    # UNSUPERVISED
    # =====================================================

    if learning_type == "unsupervised":

        if model not in unsupervised_models:
            return {
                "error": "Invalid unsupervised model.",
                "available_models": list(
                    unsupervised_models.keys()
                )
            }

        # No target column for unsupervised learning
        X = df.copy()

        # K-Means currently uses numerical columns
        X = X.select_dtypes(
            include=["int64", "float64"]
        )

        if X.empty:
            return {
                "error": "K-Means requires numerical columns."
            }

        # Remove rows containing missing values
        X = X.dropna()

        # Scale data
        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(X)

        selected_model = unsupervised_models[model]

        # Training
        start_time = time.perf_counter()

        clusters = selected_model.fit_predict(
            X_scaled
        )

        training_time = time.perf_counter() - start_time

        # Count rows in each cluster
        cluster_counts = pd.Series(
            clusters
        ).value_counts().sort_index()

        cluster_distribution = {
            f"cluster_{int(cluster)}": int(count)
            for cluster, count in cluster_counts.items()
        }

        return {
            "learning_type": "unsupervised",
            "model": model,
            "filename": file.filename,
            "rows": len(X),
            "features": len(X.columns),
            "clusters": selected_model.n_clusters,
            "training_time": round(
                training_time,
                6
            ),
            "cluster_distribution": cluster_distribution
        }