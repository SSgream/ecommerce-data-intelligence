
from pathlib import Path

import pandas as pd
import numpy as np


# =========================================================
# PATH CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# LOAD DATA
# =========================================================

print("Loading raw datasets...")

train = pd.read_csv(
    DATA_DIR / "train.csv",
    parse_dates=["date"]
)

test = pd.read_csv(
    DATA_DIR / "test.csv",
    parse_dates=["date"]
)

stores = pd.read_csv(DATA_DIR / "stores.csv")

transactions = pd.read_csv(
    DATA_DIR / "transactions.csv",
    parse_dates=["date"]
)

oil = pd.read_csv(
    DATA_DIR / "oil.csv",
    parse_dates=["date"]
)

holidays = pd.read_csv(
    DATA_DIR / "holidays_events.csv",
    parse_dates=["date"]
)

print(f"Train: {train.shape}")
print(f"Test : {test.shape}")


# =========================================================
# STORE FEATURES
# =========================================================

train_fe = train.merge(
    stores,
    on="store_nbr",
    how="left",
    validate="many_to_one"
)

test_fe = test.merge(
    stores,
    on="store_nbr",
    how="left",
    validate="many_to_one"
)


# =========================================================
# CALENDAR FEATURES
# =========================================================

def add_calendar_features(df):
    df = df.copy()

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_year"] = df["date"].dt.dayofyear

    df["week_of_year"] = (
        df["date"].dt.isocalendar().week.astype("int16")
    )

    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype("int8")

    df["quarter"] = df["date"].dt.quarter

    return df


train_fe = add_calendar_features(train_fe)
test_fe = add_calendar_features(test_fe)


# =========================================================
# TRANSACTION FEATURES
# =========================================================

train_fe = train_fe.merge(
    transactions,
    on=["date", "store_nbr"],
    how="left",
    validate="many_to_one"
)


# =========================================================
# OIL PRICE FEATURES
# =========================================================

date_range = pd.date_range(
    start=train_fe["date"].min(),
    end=test_fe["date"].max(),
    freq="D"
)

oil_daily = pd.DataFrame({"date": date_range})

oil_daily = oil_daily.merge(
    oil[["date", "dcoilwtico"]],
    on="date",
    how="left",
    validate="one_to_one"
)

oil_daily = oil_daily.sort_values("date")

oil_daily["dcoilwtico"] = (
    oil_daily["dcoilwtico"].ffill()
)

train_fe = train_fe.merge(
    oil_daily,
    on="date",
    how="left",
    validate="many_to_one"
)

test_fe = test_fe.merge(
    oil_daily,
    on="date",
    how="left",
    validate="many_to_one"
)


# =========================================================
# HOLIDAY FEATURES
# =========================================================

def build_holiday_features(stores, holidays):
    holiday_records = []

    for _, store in stores.iterrows():

        store_nbr = store["store_nbr"]

        applicable = holidays[
            (
                holidays["locale"] == "National"
            )
            |
            (
                (holidays["locale"] == "Regional")
                & (holidays["locale_name"] == store["state"])
            )
            |
            (
                (holidays["locale"] == "Local")
                & (holidays["locale_name"] == store["city"])
            )
        ].copy()

        applicable = applicable[
            ~(
                (applicable["type"] == "Holiday")
                & (applicable["transferred"] == True)
            )
        ]

        applicable["is_holiday"] = applicable["type"].isin(
            ["Holiday", "Additional", "Transfer", "Bridge"]
        )

        applicable["is_event"] = (
            applicable["type"] == "Event"
        )

        applicable["is_transfer_day"] = (
            applicable["type"] == "Transfer"
        )

        applicable["is_additional_day"] = (
            applicable["type"] == "Additional"
        )

        applicable["is_work_day"] = (
            applicable["type"] == "Work Day"
        )

        daily_features = (
            applicable.groupby("date")[
                [
                    "is_holiday",
                    "is_event",
                    "is_transfer_day",
                    "is_additional_day",
                    "is_work_day"
                ]
            ]
            .max()
            .reset_index()
        )

        daily_features["store_nbr"] = store_nbr

        holiday_records.append(daily_features)

    return pd.concat(
        holiday_records,
        ignore_index=True
    )


holiday_features = build_holiday_features(
    stores,
    holidays
)

holiday_columns = [
    "is_holiday",
    "is_event",
    "is_transfer_day",
    "is_additional_day",
    "is_work_day"
]

train_fe = train_fe.merge(
    holiday_features,
    on=["date", "store_nbr"],
    how="left",
    validate="many_to_one"
)

test_fe = test_fe.merge(
    holiday_features,
    on=["date", "store_nbr"],
    how="left",
    validate="many_to_one"
)

for col in holiday_columns:
    train_fe[col] = (
        train_fe[col].fillna(False).infer_objects(copy=False).astype("int8")
    )

    test_fe[col] = (
        test_fe[col].fillna(False).infer_objects(copy=False).astype("int8")
    )


# =========================================================
# LAG AND ROLLING FEATURES
# =========================================================

train_fe = train_fe.sort_values(
    ["store_nbr", "family", "date"]
).reset_index(drop=True)

group_cols = ["store_nbr", "family"]

for lag in [1, 7, 14, 28]:
    train_fe[f"sales_lag_{lag}"] = (
        train_fe.groupby(group_cols, sort=False)["sales"]
        .shift(lag)
        .astype("float32")
    )

for window in [7, 14, 28]:
    train_fe[f"sales_rolling_mean_{window}"] = (
        train_fe.groupby(group_cols, sort=False)["sales"]
        .transform(
            lambda x: x.shift(1).rolling(
                window=window,
                min_periods=window
            ).mean()
        )
        .astype("float32")
    )


# =========================================================
# FEATURE DEFINITIONS
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

feature_columns = (
    categorical_features + numeric_features
)

historical_features = [
    "sales_lag_1",
    "sales_lag_7",
    "sales_lag_14",
    "sales_lag_28",
    "sales_rolling_mean_7",
    "sales_rolling_mean_14",
    "sales_rolling_mean_28"
]


# =========================================================
# PREPARE MODEL DATA
# =========================================================

model_data = train_fe[
    ["date"] + feature_columns + ["sales"]
].copy()

model_data = model_data.dropna(
    subset=historical_features
)


# =========================================================
# SELECT OUTPUT COLUMNS
# =========================================================

train_output = train_fe[
    ["date"] + feature_columns + ["sales"]
].copy()

# Lag dan rolling dibuat secara bertahap
# pada proses recursive forecasting.
test_feature_columns = [
    col for col in feature_columns
    if col not in historical_features
]

test_output = test_fe[
    ["id", "date"] + test_feature_columns
].copy()


# =========================================================
# SAVE PROCESSED DATA
# =========================================================

train_path = OUTPUT_DIR / "train_features.pkl"
test_path = OUTPUT_DIR / "test_features.pkl"
model_path = OUTPUT_DIR / "model_data.pkl"

train_output.to_pickle(train_path)
test_output.to_pickle(test_path)
model_data.to_pickle(model_path)


# =========================================================
# VALIDATION
# =========================================================

print("\nFEATURE ENGINEERING COMPLETED")
print("=" * 45)

print(f"Train features : {train_output.shape}")
print(f"Test features  : {test_output.shape}")
print(f"Model data     : {model_data.shape}")

print(
    "Train date range:",
    train_output["date"].min(),
    "to",
    train_output["date"].max()
)

print(
    "Test date range:",
    test_output["date"].min(),
    "to",
    test_output["date"].max()
)

print(
    "Missing historical features:",
    model_data[historical_features].isna().sum().sum()
)

print("\nSaved files:")
print(train_path)
print(test_path)
print(model_path)
