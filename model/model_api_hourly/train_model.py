import pandas as pd
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
import numpy as np
import joblib
import os

import matplotlib.pyplot as plt

current_dir = os.path.dirname(__file__)
dataset_path = os.path.join(current_dir, "dataset_pm25.csv")

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

model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.9,
    colsample_bytree=0.8,
    objective="reg:squarederror"
)

# Train Model
model.fit(X_train, y_train)
preds = model.predict(X_test)          # predict ผล (ค่าฝุ่นที่โมเดลทำนายในช่วง test set)

plt.figure(figsize=(10,4))
plt.plot(y_test.values, label="Actual PM2.5")
plt.plot(preds, label="Predicted PM2.5")
plt.title("Actual vs Predicted PM2.5 (Test Set)")
plt.xlabel("Time (test index)")
plt.ylabel("PM2.5")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(current_dir, "pm25_actual_vs_pred.png"))   # บันทึกไฟล์
plt.show()


result_df = pd.DataFrame({
    "actual": y_test.values,
    "predicted": preds
})

print(result_df.head(20))

mae = mean_absolute_error(y_test, preds)
rmse = np.sqrt(np.mean((y_test - preds)**2))

print("MAE =", mae)
print("RMSE =", rmse)

# save model
joblib.dump(model, os.path.join(current_dir, "pm25_model.pkl"))
print(f"Saved model -> {os.path.join(current_dir, 'pm25_model.pkl')}")
