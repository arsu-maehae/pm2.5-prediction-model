import pandas as pd
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
import numpy as np
import joblib
import os

import matplotlib.pyplot as plt

current_dir = os.path.dirname(__file__)
dataset_path = os.path.join(current_dir, "dataset_pm25_full.csv")

df = pd.read_csv(dataset_path, index_col=0)

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

# ปรับ hyperparameters ให้ดีขึ้น
model = XGBRegressor(
    n_estimators=500,  # เพิ่มจำนวน trees
    learning_rate=0.03,  # ลด learning rate
    max_depth=8,  # เพิ่ม depth
    subsample=0.9,
    colsample_bytree=0.8,
    random_state=42
)

# Train Model
model.fit(X_train, y_train)
preds = model.predict(X_test)

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
results_path = os.path.join(current_dir, "prediction_results_full.csv")
results_df.to_csv(results_path, index=True)
print(f"Results saved to {results_path}")

# แสดงตัวอย่างตาราง
print("\nSample Results:")
print(results_df.head(10).to_markdown(index=True))

# บันทึกโมเดล
model_path = os.path.join(current_dir, "model_full.pkl")
joblib.dump(model, model_path)
print(f"Model saved to {model_path}")

# Plot
plt.figure(figsize=(10,4))
plt.plot(y_test.values[:100], label="Actual PM2.5")  # แสดงแค่ 100 จุดแรก
plt.plot(preds[:100], label="Predicted PM2.5")
plt.title("Actual vs Predicted PM2.5 (Full Dataset - First 100 points)")
plt.xlabel("Time (test index)")
plt.ylabel("PM2.5")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(current_dir, "pm25_actual_vs_pred_full.png"))
print("Plot saved.")

print("Model training completed for full dataset.")