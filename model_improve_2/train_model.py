import pandas as pd
import numpy as np
import os
import joblib
import optuna

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor
import matplotlib.pyplot as plt


# ===============================
# READ DATA (automatic path)
# ===============================
current_dir = os.path.dirname(__file__)
dataset_path = os.path.join(current_dir, "dataset_pm25.csv")

df = pd.read_csv(dataset_path)

# เลือกเฉพาะตัวเลข (รวม weekend & rolling feature)
numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
numeric_cols = [c for c in numeric_cols if c != "target_pm25"]

X = df[numeric_cols]
y = df["target_pm25"]


# ===============================
# OPTUNA TUNING FUNCTION
# ===============================
def objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 200, 800),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.0, 5.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 5.0),
        "objective": "reg:squarederror",
        "random_state": 42
    }

    model = XGBRegressor(**params)

    # Time-series cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    maes = []

    for train_idx, valid_idx in tscv.split(X):
        X_train, X_valid = X.iloc[train_idx], X.iloc[valid_idx]
        y_train, y_valid = y.iloc[train_idx], y.iloc[valid_idx]

        model.fit(X_train, y_train)
        preds = model.predict(X_valid)
        mae = mean_absolute_error(y_valid, preds)
        maes.append(mae)

    return np.mean(maes)


# ===============================
# RUN OPTUNA (TUNING)
# ===============================
print("\n🔥 Running Optuna hyperparameter tuning (please wait)...")
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=30)

print("\n🎉 Best parameters found:")
print(study.best_params)


# ===============================
# TRAIN FINAL MODEL
# ===============================
best_params = study.best_params
best_params["objective"] = "reg:squarederror"
best_params["random_state"] = 42

model = XGBRegressor(**best_params)
model.fit(X, y)

save_path = os.path.join(current_dir, "pm25_model_optimized.pkl")
joblib.dump(model, save_path)

print(f"\n💾 Saved optimized model → {save_path}")


# ===============================
# PLOT FEATURE IMPORTANCE
# ===============================
plt.figure(figsize=(10, 6))
plt.barh(model.feature_names_in_, model.feature_importances_)
plt.title("Feature Importance")
plt.tight_layout()
plt.savefig(os.path.join(current_dir, "feature_importance.png"))
# plt.show()


# ===============================
# TRAIN-TEST SPLIT (Last 10% for testing)
# ===============================
test_size = int(len(df) * 0.1)
X_train, X_test = X[:-test_size], X[-test_size:]
y_train, y_test = y[:-test_size], y[-test_size:]

model.fit(X_train, y_train)
preds = model.predict(X_test)

mae = mean_absolute_error(y_test, preds)
rmse = mean_squared_error(y_test, preds) ** 0.5

print("\n📊 Final Evaluation on Test Set:")
print(f"MAE  = {mae}")
print(f"RMSE = {rmse}")

# ===============================
# PLOT ACTUAL vs PREDICTED
# ===============================
plt.figure(figsize=(12, 5))
plt.plot(y_test.values, label="Actual PM2.5")
plt.plot(preds, label="Predicted PM2.5")
plt.legend()
plt.xlabel("Time index (test set)")
plt.ylabel("PM2.5")
plt.title("Actual vs Predicted PM2.5")
plt.savefig(os.path.join(current_dir, "pm25_actual_vs_pred_optimized.png"))
plt.show()



result_df = pd.DataFrame({
    "actual": y_test.values,
    "predicted": preds
})

print(result_df.head(20))

