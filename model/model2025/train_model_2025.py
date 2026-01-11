import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GridSearchCV
from xgboost import XGBRegressor
import numpy as np
import joblib
import os

import matplotlib.pyplot as plt

current_dir = os.path.dirname(__file__)
dataset_path = os.path.join(current_dir, "dataset_pm25_2025.csv")

df = pd.read_csv(dataset_path)

# เลือกเฉพาะตัวเลขเท่านั้น
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

# เอา target ออกจาก X
numeric_cols = [c for c in numeric_cols if c != "target_pm25"]

X = df[numeric_cols]
y = df["target_pm25"]

# train-test split แบบ time-series
train_size = int(len(df) * 0.8)
X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

# Hyperparameter tuning with GridSearchCV
param_grid = {
    'n_estimators': [100, 300, 500],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [4, 6, 8],
    'subsample': [0.8, 0.9],
    'colsample_bytree': [0.8, 0.9]
}

xgb = XGBRegressor(objective="reg:squarederror", random_state=42)
grid_search = GridSearchCV(estimator=xgb, param_grid=param_grid, cv=3, scoring='neg_mean_absolute_error', verbose=1)
grid_search.fit(X_train, y_train)

# Best model
model = grid_search.best_estimator_
print(f"Best parameters: {grid_search.best_params_}")
print(f"Best CV MAE: {-grid_search.best_score_:.2f}")
preds = model.predict(X_test)          # predict ผล (ค่าฝุ่นที่โมเดลทำนายในช่วง test set)

plt.figure(figsize=(10,4))
plt.plot(y_test.values, label="Actual PM2.5")
plt.plot(preds, label="Predicted PM2.5")
plt.title("Actual vs Predicted PM2.5 (Test Set - 2025)")
plt.xlabel("Time (test index)")
plt.ylabel("PM2.5")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(current_dir, "pm25_actual_vs_pred_2025.png"))   # บันทึกไฟล์

# วัดความแม่นยำ
mae = mean_absolute_error(y_test, preds)
print(f"Mean Absolute Error (MAE): {mae:.2f}")

# สร้างตารางเปรียบเทียบ
results_df = pd.DataFrame({
    'Actual_PM25': y_test.values,
    'Predicted_PM25': preds,
    'Absolute_Error': abs(y_test.values - preds),
    'Percentage_Error': (abs(y_test.values - preds) / y_test.values) * 100
})

# บันทึกตาราง
results_path = os.path.join(current_dir, "prediction_results_2025.csv")
results_df.to_csv(results_path, index=True)
print(f"Results saved to {results_path}")

# แสดงตัวอย่างตาราง
print("\nSample Results:")
print(results_df.head(10).to_markdown(index=True))

# บันทึกโมเดล
model_path = os.path.join(current_dir, "model_2025.pkl")
joblib.dump(model, model_path)
print(f"Model saved to {model_path}")

print("Model training completed for 2025 data.")