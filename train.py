"""
Model training script for the AI Educational Schemes Recommendation System.
Trains a RandomForestRegressor on generated student-scheme pairs and saves 
the model artifact alongside evaluation metrics.
"""

import os
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from eligibility_engine import load_schemes
from features import generate_citizens, build_training_pairs, encode_features


def train():
    print("Loading educational schemes dataset...")
    schemes_path = "data/educational_schemes_min_marks_cleaned.csv"
    schemes_df = load_schemes(schemes_path)

    # Extract unique state names from state-level schemes
    states = sorted(
        schemes_df.loc[schemes_df["level"] == "State", "state"].dropna().unique().tolist()
    )

    print("Generating synthetic student profiles and building training pairs...")
    citizens_df = generate_citizens(n=500, states=states, seed=42)
    pairs_df = build_training_pairs(citizens_df, schemes_df)

    # Filter to eligible pairs only for training the regression model
    eligible_pairs = pairs_df[pairs_df["eligible"] == 1].copy()
    print(f"Total eligible student-scheme pairs for training: {len(eligible_pairs)}")

    # Encode features for training
    encoded_df = encode_features(eligible_pairs)

    # Define target and features
    y = encoded_df["match_score"]
    X = encoded_df.drop(columns=["eligible", "match_score"], errors="ignore")

    # Split dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Training Random Forest Regressor model...")
    regressor = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )
    regressor.fit(X_train, y_train)

    # Evaluate model performance
    y_pred = regressor.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n--- Model Performance ---")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"Mean Squared Error (MSE):  {mse:.4f}")
    print(f"R² Score:                 {r2:.4f}")

    # Ensure output directories exist
    os.makedirs("models", exist_ok=True)

    # Save trained model and expected column format
    model_path = "models/match_score_regressor.joblib"
    joblib.dump(
        {"model": regressor, "columns": list(X.columns)},
        model_path
    )
    print(f"Saved trained model to {model_path}")

    # Save metrics JSON for Streamlit Analytics Dashboard display
    metrics = {
        "RandomForestRegressor": {
            "MAE": round(mae, 4),
            "MSE": round(mse, 4),
            "R2 Score": round(r2, 4)
        }
    }
    metrics_path = "models/metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)
    print(f"Saved evaluation metrics to {metrics_path}")


if __name__ == "__main__":
    train()