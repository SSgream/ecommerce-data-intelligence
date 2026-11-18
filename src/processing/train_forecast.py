
from pathlib import Path
from collections import defaultdict
import time

import joblib

import numpy as np
import pandas as pd

from sklearn.preprocessing import OrdinalEncoder
from xgboost import XGBRegressor

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)
from pathlib import Path


# =========================================================
# PATH CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODEL_DATA_PATH = PROCESSED_DIR / "model_data.pkl"
TRAIN_FEATURES_PATH = PROCESSED_DIR / "train_features.pkl"
TEST_FEATURES_PATH = PROCESSED_DIR / "test_features.pkl"

OUTPUT_PATH = PROCESSED_DIR / "sales_forecast_candidate.csv"
EXISTING_FORECAST_PATH = PROCESSED_DIR / "sales_forecast.csv"


# =========================================================
# LOAD PROCESSED DATA
# =========================================================

print("Loading processed datasets...")

model_data = pd.read_pickle(MODEL_DATA_PATH)
train_fe = pd.read_pickle(TRAIN_FEATURES_PATH)
test_fe = pd.read_pickle(TEST_FEATURES_PATH)

print("Model data:", model_data.shape)
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
target = "sales"


# =========================================================
# VALIDATE INPUT DATA
# =========================================================

required_model_columns = (
    ["date"] + feature_columns + [target]
)

required_train_columns = [
    "date",
    "store_nbr",
    "family",
    "sales"
]

required_test_columns = (
    ["id", "date"] +
    [
        col for col in feature_columns
        if col not in historical_features
    ]
)

for col in required_model_columns:
    if col not in model_data.columns:
        raise ValueError(f"Missing model_data column: {col}")

for col in required_train_columns:
    if col not in train_fe.columns:
        raise ValueError(f"Missing train_features column: {col}")

for col in required_test_columns:
    if col not in test_fe.columns:
        raise ValueError(f"Missing test_features column: {col}")

print("\nInput validation passed.")


# =========================================================
# TRAIN / VALIDATION SPLIT
# =========================================================

validation_start = pd.Timestamp("2017-07-17")
validation_end = pd.Timestamp("2017-08-15")

train_model = model_data[
    model_data["date"] < validation_start
].copy()

valid_model = model_data[
    (model_data["date"] >= validation_start) &
    (model_data["date"] <= validation_end)
].copy()

print("\nTRAINING DATA")
print("=" * 40)

print("Training records:", len(train_model))
print("Validation records:", len(valid_model))

print(
    "Training period:",
    train_model["date"].min(),
    "to",
    train_model["date"].max()
)

print(
    "Validation period:",
    valid_model["date"].min(),
    "to",
    valid_model["date"].max()
)


# =========================================================
# ORDINAL ENCODING
# =========================================================

encoder = OrdinalEncoder(
    handle_unknown="use_encoded_value",
    unknown_value=-1
)

X_train = train_model[feature_columns].copy()
X_valid = valid_model[feature_columns].copy()

X_train[categorical_features] = encoder.fit_transform(
    X_train[categorical_features]
)

X_valid[categorical_features] = encoder.transform(
    X_valid[categorical_features]
)

y_train = train_model[target].copy()
y_valid = valid_model[target].copy()

print("\nEncoding completed.")
print("X_train:", X_train.shape)
print("X_valid:", X_valid.shape)


import hashlib

def dataframe_hash(df):
    return hashlib.sha256(
        pd.util.hash_pandas_object(
            df, index=True
        ).values.tobytes()
    ).hexdigest()

def series_hash(series):
    return hashlib.sha256(
        pd.util.hash_pandas_object(
            series, index=True
        ).values.tobytes()
    ).hexdigest()

print("\nDATA CONSISTENCY CHECK")
print("=" * 50)

print("Feature columns:")
print(list(X_train.columns))

print("\nData types:")
print(X_train.dtypes.value_counts())

print("\nTraining feature hash:")
print(dataframe_hash(X_train))

print("\nTraining target hash:")
print(series_hash(y_train))

print("\nValidation feature hash:")
print(dataframe_hash(X_valid))

print("\nValidation target hash:")
print(series_hash(y_valid))

print("\nTraining target statistics:")
print(y_train.describe())

print("\nValidation target statistics:")
print(y_valid.describe())



# =========================================================
# XGBOOST MODEL
# =========================================================

xgb_model = XGBRegressor(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    tree_method="hist",
    n_jobs=1,
    random_state=42
)

print("\nTraining XGBoost model...")

start_time = time.time()

xgb_model.fit(
    X_train,
    y_train,
    verbose=False
)

training_time = time.time() - start_time

print(f"Training completed in {training_time:.2f} seconds")


print("NOTEBOOK XGBOOST CONFIG")
print("=" * 50)

print(xgb_model.get_params(deep=False))
print("\nBOOSTER CONFIG:")
print(xgb_model.get_booster().save_config())


import hashlib

script_predictions = xgb_model.predict(X_valid)

print("\nSCRIPT MODEL CHECK")
print("=" * 50)

print("Prediction hash:")
print(
    hashlib.sha256(
        script_predictions.tobytes()
    ).hexdigest()
)

print("\nPrediction statistics:")
print(pd.Series(script_predictions).describe())

print("\nFirst 10 predictions:")
print(script_predictions[:10])

# ==========================================
# SAVE MODEL ARTIFACTS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = PROJECT_ROOT / "data_science" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

joblib.dump(
    xgb_model,
    MODEL_DIR / "xgb_model.joblib"
)

joblib.dump(
    encoder,
    MODEL_DIR / "ordinal_encoder.joblib"
)

print("\nMODEL ARTIFACTS SAVED")
print("=" * 40)
print("XGBoost model :", MODEL_DIR / "xgb_model.joblib")
print("Ordinal encoder:", MODEL_DIR / "ordinal_encoder.joblib")

# =========================================================
# VALIDATION METRICS
# =========================================================

y_pred = xgb_model.predict(X_valid)

rmse = np.sqrt(mean_squared_error(y_valid, y_pred))
mae = mean_absolute_error(y_valid, y_pred)
r2 = r2_score(y_valid, y_pred)

print("\nMODEL VALIDATION METRICS")
print("=" * 40)
print(f"RMSE: {rmse:.6f}")
print(f"MAE : {mae:.6f}")
print(f"R2  : {r2:.6f}")


# =========================================================
# RECURSIVE FORECASTING
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

test_recursive_results = []

test_dates = sorted(test_fe["date"].unique())

print("\nStarting recursive forecasting...")
forecast_start_time = time.time()

for date_number, current_date in enumerate(test_dates, start=1):

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
    raise ValueError("Forecast record count does not match test data.")

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


# =========================================================
# COMPARE WITH EXISTING FORECAST
# =========================================================

if EXISTING_FORECAST_PATH.exists():

    print("\nCOMPARING WITH EXISTING FORECAST")
    print("=" * 40)

    existing_forecast = pd.read_csv(
        EXISTING_FORECAST_PATH
    )

    comparison = existing_forecast[
        ["id", "predicted_sales"]
    ].merge(
        test_forecast[
            ["id", "predicted_sales"]
        ],
        on="id",
        how="outer",
        suffixes=("_old", "_new"),
        indicator=True
    )

    matched_ids = (
        comparison["_merge"] == "both"
    ).sum()

    exact_matches = (
        comparison.loc[
            comparison["_merge"] == "both",
            "predicted_sales_old"
        ]
        ==
        comparison.loc[
            comparison["_merge"] == "both",
            "predicted_sales_new"
        ]
    ).sum()

    max_difference = (
        comparison.loc[
            comparison["_merge"] == "both"
        ]
        .eval("abs(predicted_sales_old - predicted_sales_new)")
        .max()
    )
    
    matched = comparison[
        comparison["_merge"] == "both"
    ].copy()

    matched["abs_diff"] = (
        matched["predicted_sales_old"]
        - matched["predicted_sales_new"]
    ).abs()

    print("\nPrediction difference statistics:")
    print(matched["abs_diff"].describe())

    print("\nFirst 10 predictions:")
    print(
        matched[
            [
                "id",
                "predicted_sales_old",
                "predicted_sales_new",
                "abs_diff"
            ]
        ].head(10).to_string(index=False)
    )

    print("Existing records:", len(existing_forecast))
    print("New records:", len(test_forecast))
    print("Matched IDs:", matched_ids)
    print("Exact prediction matches:", exact_matches)
    print("Maximum absolute difference:", max_difference)

    if matched_ids == len(test_forecast) and exact_matches == len(test_forecast):
        print("\nRESULT: Forecast matches the existing CSV exactly.")
    else:
        print("\nRESULT: Forecast differs from the existing CSV.")
        print("Existing CSV has NOT been overwritten.")

else:
    print("\nExisting forecast CSV not found. Comparison skipped.")


print("\nPIPELINE TRAINING AND FORECASTING FINISHED.")
print(f"Model training time: {training_time:.2f} seconds")
print(f"Forecasting time: {forecast_time:.2f} seconds")


# ==========================================
# ANALISIS PERBEDAAN FORECAST
# ==========================================

old_df = pd.read_csv(
    PROCESSED_DIR / "sales_forecast.csv"
)

new_df = pd.read_csv(
    PROCESSED_DIR / "sales_forecast_candidate.csv"
)

comparison = old_df.merge(
    new_df,
    on=["id", "date", "store_nbr", "family"],
    suffixes=("_old", "_new")
)

comparison["abs_diff"] = (
    comparison["predicted_sales_old"]
    - comparison["predicted_sales_new"]
).abs()

print("\n10 PREDIKSI DENGAN SELISIH TERBESAR")
print("=" * 70)

print(
    comparison.nlargest(10, "abs_diff")[
        [
            "date",
            "store_nbr",
            "family",
            "predicted_sales_old",
            "predicted_sales_new",
            "abs_diff"
        ]
    ].to_string(index=False)
)

print("\nRATA-RATA SELISIH BERDASARKAN TANGGAL")
print("=" * 70)

daily_diff = (
    comparison.groupby("date")["abs_diff"]
    .agg(["mean", "max"])
    .reset_index()
)

print(daily_diff.to_string(index=False))

print("\nRATA-RATA SELISIH BERDASARKAN FAMILY")
print("=" * 70)

family_diff = (
    comparison.groupby("family")["abs_diff"]
    .mean()
    .sort_values(ascending=False)
)

print(family_diff.head(10).to_string())
