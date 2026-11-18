
from pathlib import Path
from collections import defaultdict
import time

import joblib
import numpy as np
import pandas as pd


# =========================================================
# PATH CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "data_science" / "models"

TRAIN_FEATURES_PATH = PROCESSED_DIR / "train_features.pkl"
TEST_FEATURES_PATH = PROCESSED_DIR / "test_features.pkl"

MODEL_PATH = MODEL_DIR / "xgb_model.joblib"
ENCODER_PATH = MODEL_DIR / "ordinal_encoder.joblib"

OUTPUT_PATH = PROCESSED_DIR / "sales_forecast_candidate.csv"


# =========================================================
# LOAD MODEL ARTIFACTS
# =========================================================

print("Loading model artifacts...")

xgb_model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

print("Model:", type(xgb_model).__name__)
print("Encoder:", type(encoder).__name__)
print("Number of features:", xgb_model.n_features_in_)


# =========================================================
# LOAD PROCESSED DATA
# =========================================================

print("\nLoading processed datasets...")

train_fe = pd.read_pickle(TRAIN_FEATURES_PATH)
test_fe = pd.read_pickle(TEST_FEATURES_PATH)

print("Train features:", train_fe.shape)
print("Test features:", test_fe.shape)


# =========================================================
# FEATURE CONFIGURATION
# =========================================================

categorical_features = [
    "store_nbr",
    "family",
    "city",
    "state",
    "type",
    "cluster"
]

numeric_features = [
    "onpromotion",
    "year",
    "month",
    "day",
    "day_of_week",
    "day_of_year",
    "week_of_year",
    "is_weekend",
    "quarter",
    "dcoilwtico",
    "is_holiday",
    "is_event",
    "is_transfer_day",
    "is_additional_day",
    "is_work_day",
    "sales_lag_1",
    "sales_lag_7",
    "sales_lag_14",
    "sales_lag_28",
    "sales_rolling_mean_7",
    "sales_rolling_mean_14",
    "sales_rolling_mean_28"
]

historical_features = [
    "sales_lag_1",
    "sales_lag_7",
    "sales_lag_14",
    "sales_lag_28",
    "sales_rolling_mean_7",
    "sales_rolling_mean_14",
    "sales_rolling_mean_28"
]

feature_columns = categorical_features + numeric_features


# =========================================================
# VALIDATE INPUT DATA
# =========================================================

required_train_columns = [
    "store_nbr",
    "family",
    "date",
    "sales"
]

required_test_columns = (
    ["id", "date"] +
    [
        col for col in feature_columns
        if col not in historical_features
    ]
)

for col in required_train_columns:
    if col not in train_fe.columns:
        raise ValueError(
            f"Missing train_features column: {col}"
        )

for col in required_test_columns:
    if col not in test_fe.columns:
        raise ValueError(
            f"Missing test_features column: {col}"
        )

if len(feature_columns) != xgb_model.n_features_in_:
    raise ValueError("Model feature count does not match.")

print("\nInput validation passed.")


# =========================================================
# PREPARE HISTORICAL SALES
# =========================================================

print("\nPreparing historical sales...")

history_test = defaultdict(list)

history_data_test = (
    train_fe[
        ["store_nbr", "family", "date", "sales"]
    ]
    .sort_values(["store_nbr", "family", "date"])
)

for (store, family), group in history_data_test.groupby(
    ["store_nbr", "family"]
):
    history_test[(store, family)] = (
        group["sales"].astype(float).tolist()
    )

print("Number of series:", len(history_test))


# =========================================================
# RECURSIVE FORECASTING
# =========================================================

test_recursive_results = []

test_dates = sorted(test_fe["date"].unique())

print("\nStarting recursive forecasting...")

forecast_start_time = time.time()

for date_number, current_date in enumerate(
    test_dates,
    start=1
):

    day_data = test_fe.loc[
        test_fe["date"] == current_date
    ].copy()

    day_data = day_data.sort_values(
        ["store_nbr", "family"]
    )

    # Build lag and rolling features from history
    for idx, row in day_data.iterrows():

        key = (row["store_nbr"], row["family"])
        hist = history_test[key]

        day_data.at[idx, "sales_lag_1"] = hist[-1]
        day_data.at[idx, "sales_lag_7"] = hist[-7]
        day_data.at[idx, "sales_lag_14"] = hist[-14]
        day_data.at[idx, "sales_lag_28"] = hist[-28]

        day_data.at[idx, "sales_rolling_mean_7"] = np.mean(
            hist[-7:]
        )

        day_data.at[idx, "sales_rolling_mean_14"] = np.mean(
            hist[-14:]
        )

        day_data.at[idx, "sales_rolling_mean_28"] = np.mean(
            hist[-28:]
        )

    # Prepare model input
    X_day = day_data[feature_columns].copy()

    X_day[categorical_features] = encoder.transform(
        X_day[categorical_features]
    )

    # Predict and constrain minimum to zero
    day_pred = np.maximum(
        xgb_model.predict(X_day),
        0
    )

    # Save daily forecast
    day_result = day_data[
        ["id", "date", "store_nbr", "family"]
    ].copy()

    day_result["predicted_sales"] = day_pred

    test_recursive_results.append(day_result)

    # Feed predictions into history for the next day
    keys = day_data[
        ["store_nbr", "family"]
    ].itertuples(index=False, name=None)

    for key, prediction in zip(keys, day_pred):
        history_test[key].append(float(prediction))

    print(
        f"Day {date_number}/{len(test_dates)} completed:",
        pd.Timestamp(current_date).date()
    )


forecast_time = time.time() - forecast_start_time


# =========================================================
# COMBINE FORECAST RESULTS
# =========================================================

test_forecast = pd.concat(
    test_recursive_results,
    ignore_index=True
)

print("\nTEST FORECAST COMPLETED")
print("=" * 40)

print("Total records:", len(test_forecast))
print("First date:", test_forecast["date"].min())
print("Last date:", test_forecast["date"].max())
print(f"Forecast runtime: {forecast_time:.2f} seconds")


# =========================================================
# FORECAST VALIDATION
# =========================================================

print("\nFORECAST DATA VALIDATION")
print("=" * 40)

duplicate_ids = test_forecast["id"].duplicated().sum()

duplicate_grain = test_forecast.duplicated(
    ["date", "store_nbr", "family"]
).sum()

missing_values = test_forecast.isna().sum().sum()

negative_predictions = (
    test_forecast["predicted_sales"] < 0
).sum()

print("Expected records:", len(test_fe))
print("Actual records:", len(test_forecast))
print("Duplicate IDs:", duplicate_ids)
print("Duplicate date-store-family:", duplicate_grain)
print("Missing values:", missing_values)
print("Negative predictions:", negative_predictions)
print("Unique dates:", test_forecast["date"].nunique())
print("Unique stores:", test_forecast["store_nbr"].nunique())
print("Unique families:", test_forecast["family"].nunique())

if len(test_forecast) != len(test_fe):
    raise ValueError(
        "Forecast record count does not match test data."
    )

if duplicate_ids > 0 or duplicate_grain > 0:
    raise ValueError("Duplicate forecast records detected.")

if missing_values > 0:
    raise ValueError("Missing values detected in forecast.")

if negative_predictions > 0:
    raise ValueError("Negative predictions detected.")

print("\nAll forecast validation checks passed.")


# =========================================================
# SAVE CANDIDATE FORECAST
# =========================================================

test_forecast.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nCandidate forecast saved:")
print(OUTPUT_PATH)

print("\nFORECAST PIPELINE FINISHED.")
print(f"Forecasting time: {forecast_time:.2f} seconds")
