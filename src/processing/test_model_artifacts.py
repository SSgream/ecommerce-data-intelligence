
from pathlib import Path
import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "data_science" / "models"

# Load model dan encoder
xgb_model = joblib.load(MODEL_DIR / "xgb_model.joblib")
encoder = joblib.load(MODEL_DIR / "ordinal_encoder.joblib")

print("MODEL ARTIFACT VALIDATION")
print("=" * 45)

print("Model type:", type(xgb_model).__name__)
print("Encoder type:", type(encoder).__name__)
print("Number of estimators:", xgb_model.n_estimators)
print("Number of features:", xgb_model.n_features_in_)
print("Encoder categories:", len(encoder.categories_))

# Periksa kemampuan prediksi dengan satu baris data validasi
data_path = PROJECT_ROOT / "data" / "processed" / "model_data.pkl"
model_data = pd.read_pickle(data_path)

categorical_features = [
    "store_nbr", "family", "city",
    "state", "type", "cluster"
]

feature_columns = [
    "store_nbr", "family", "city", "state", "type", "cluster",
    "onpromotion", "year", "month", "day", "day_of_week",
    "day_of_year", "week_of_year", "is_weekend", "quarter",
    "dcoilwtico", "is_holiday", "is_event", "is_transfer_day",
    "is_additional_day", "is_work_day", "sales_lag_1",
    "sales_lag_7", "sales_lag_14", "sales_lag_28",
    "sales_rolling_mean_7", "sales_rolling_mean_14",
    "sales_rolling_mean_28"
]

sample = model_data[feature_columns].iloc[[0]].copy()
sample[categorical_features] = encoder.transform(
    sample[categorical_features]
)

prediction = xgb_model.predict(sample)

print("\nPrediction test:", prediction[0])
print("\nAll artifact checks passed.")
